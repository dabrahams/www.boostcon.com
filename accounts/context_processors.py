def account_messages(request):
    msg = request.session.get('account_message')
    if msg:
        del request.session['account_message']
    return {
        'account_message': msg or ''
    }

