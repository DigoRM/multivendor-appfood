def detectUser(user):
    if user.role == 1:
        redirectUrl = 'vendorDashboard'
    elif user.role == 2:
        redirectUrl = 'custDashboard'
    elif user.is_superadmin:
        redirectUrl = '/admin'
    else:
        redirectUrl = '/' # or whatever default URL you want to use
    return redirectUrl