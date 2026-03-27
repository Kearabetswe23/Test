from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.utils import timezone

from .models import IssueReport, Message, Notification
from .forms import IssueReportForm, MessageForm, StatusUpdateForm, ReportFilterForm


def create_notification(user, title, message_text, report=None):
    """Helper to create a notification for a user."""
    Notification.objects.create(
        user=user,
        title=title,
        message=message_text,
        report=report
    )


@login_required
def dashboard(request):
    """Main dashboard showing stats and recent reports."""
    user = request.user

    # Get reports based on role
    try:
        is_official = user.profile.is_official()
    except Exception:
        is_official = False

    if is_official:
        all_reports = IssueReport.objects.all()
    else:
        all_reports = IssueReport.objects.filter(reporter=user)

    # Stats
    stats = {
        'total': all_reports.count(),
        'submitted': all_reports.filter(status='submitted').count(),
        'in_progress': all_reports.filter(status='in_progress').count(),
        'resolved': all_reports.filter(status='resolved').count(),
        'urgent': all_reports.filter(priority='urgent').count(),
    }

    recent_reports = all_reports[:5]
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()

    # Unread messages count
    unread_messages = Message.objects.filter(
        report__reporter=user,
        is_read=False
    ).exclude(sender=user).count()

    return render(request, 'reports/dashboard.html', {
        'stats': stats,
        'recent_reports': recent_reports,
        'is_official': is_official,
        'unread_notifications': unread_notifications,
        'unread_messages': unread_messages,
    })


@login_required
def report_list(request):
    """List all reports with filtering."""
    user = request.user
    try:
        is_official = user.profile.is_official()
    except Exception:
        is_official = False

    if is_official:
        reports = IssueReport.objects.all()
    else:
        reports = IssueReport.objects.filter(reporter=user)

    # Apply filters
    form = ReportFilterForm(request.GET)
    if form.is_valid():
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        search = form.cleaned_data.get('search')

        if category:
            reports = reports.filter(category=category)
        if status:
            reports = reports.filter(status=status)
        if search:
            reports = reports.filter(
                Q(title__icontains=search) | Q(location__icontains=search)
            )

    return render(request, 'reports/report_list.html', {
        'reports': reports,
        'filter_form': form,
        'is_official': is_official,
    })


@login_required
def report_create(request):
    """Create a new issue report."""
    if request.method == 'POST':
        form = IssueReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            # Auto-fill ward from profile if not provided
            if not report.ward_number:
                try:
                    report.ward_number = request.user.profile.ward_number
                except Exception:
                    pass
            report.save()

            messages.success(request,
                f'✅ Report submitted! Your reference number is {report.reference_number}.')
            return redirect('reports:report_detail', pk=report.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill ward from profile
        initial = {}
        try:
            initial['ward_number'] = request.user.profile.ward_number
        except Exception:
            pass
        form = IssueReportForm(initial=initial)

    return render(request, 'reports/report_form.html', {'form': form, 'title': 'Report an Issue'})


@login_required
def report_detail(request, pk):
    """View a report's details and its messages."""
    report = get_object_or_404(IssueReport, pk=pk)
    user = request.user

    try:
        is_official = user.profile.is_official()
    except Exception:
        is_official = False

    # Only reporter or officials can view
    if report.reporter != user and not is_official:
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('reports:report_list')

    # Mark messages as read
    report.messages.exclude(sender=user).update(is_read=True)

    # Handle message submission
    msg_form = MessageForm()
    if request.method == 'POST' and 'send_message' in request.POST:
        msg_form = MessageForm(request.POST)
        if msg_form.is_valid():
            msg = msg_form.save(commit=False)
            msg.report = report
            msg.sender = user
            msg.is_official_response = is_official
            msg.save()

            # Notify the other party
            if is_official:
                create_notification(
                    report.reporter,
                    f'New response on {report.reference_number}',
                    f'A municipal official has responded to your report: "{report.title}"',
                    report
                )
            else:
                # Notify assigned official if any
                if report.assigned_to:
                    create_notification(
                        report.assigned_to,
                        f'New message on {report.reference_number}',
                        f'The resident has sent a message regarding: "{report.title}"',
                        report
                    )

            messages.success(request, 'Message sent successfully.')
            return redirect('reports:report_detail', pk=pk)

    # Handle status update (officials only)
    status_form = StatusUpdateForm(instance=report)
    if request.method == 'POST' and 'update_status' in request.POST and is_official:
        status_form = StatusUpdateForm(request.POST, instance=report)
        if status_form.is_valid():
            old_status = report.status
            updated = status_form.save()
            # Notify reporter
            create_notification(
                report.reporter,
                f'Status update: {report.reference_number}',
                f'Your report "{report.title}" status changed from '
                f'{old_status} to {updated.status}.',
                report
            )
            messages.success(request, '✅ Report status updated.')
            return redirect('reports:report_detail', pk=pk)

    chat_messages = report.messages.all()

    return render(request, 'reports/report_detail.html', {
        'report': report,
        'chat_messages': chat_messages,
        'msg_form': msg_form,
        'status_form': status_form,
        'is_official': is_official,
    })


@login_required
def notifications_view(request):
    """View all notifications for the logged-in user."""
    notifs = Notification.objects.filter(user=request.user)
    # Mark all as read when page is opened
    notifs.update(is_read=True)
    return render(request, 'reports/notifications.html', {'notifications': notifs})


@login_required
def messages_inbox(request):
    """Inbox: show all reports the user has messages on."""
    user = request.user
    try:
        is_official = user.profile.is_official()
    except Exception:
        is_official = False

    if is_official:
        # Officials see all reports with messages
        reports_with_messages = IssueReport.objects.filter(
            messages__isnull=False
        ).distinct().annotate(msg_count=Count('messages')).order_by('-updated_at')
    else:
        reports_with_messages = IssueReport.objects.filter(
            reporter=user,
            messages__isnull=False
        ).distinct().annotate(msg_count=Count('messages')).order_by('-updated_at')

    return render(request, 'reports/messages_inbox.html', {
        'reports': reports_with_messages,
        'is_official': is_official,
    })
