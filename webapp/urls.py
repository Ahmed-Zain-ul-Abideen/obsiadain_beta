# urls.py
from django.urls import path
from   webapp.Views.Mills_related.register_mill  import    *
from   webapp.Views.Users_signup_nd_login.user_signup   import   register_user
from  webapp.Views.Users_signup_nd_login.user_login   import   login_view,  logout_view, index , view_users_login_logout_activities_log
from   webapp.Views.Maps.all_maps   import  *
from   webapp.Views.master_adm.master_control    import  *
from  webapp.Views.Payments.all_paym   import   *
from  webapp.Views.Others.others   import  *
from  webapp.Views.Users_signup_nd_login.set_pass   import   set_password_view
from   webapp.Chat.for_chats   import   *
from   webapp.Views.Invoices.all_nvcs   import   *
from  webapp.Views.Invoices.thr_xhtmpd   import  generate_invoice_pdf

urlpatterns = [
    # Landing Page
    path('', index, name='index'),  # root = index (landing page)
    #Auths
    path('login/', login_view, name='login'),  # root = login
    path('register/', register_user, name='register'),
    path('logout/', logout_view, name='logout'),

    #Mills
    path('add-mill-by-owner/', register_mill_by_owner, name='add_mill_by_owner'),
    path('add-mill-by-fbr-official/', register_mill_by_fbr_official, name='add_mill_by_fbr_official'),
    path('view-mills/', view_mills, name='view_mills'),
    path("edit-mill/<int:unit_id>/", edit_mill_unit, name="edit_mill_unit"),
    path("edit-mill-only/<int:mill_id>/", edit_mill_only, name="edit_mill_only"),
    path("add-unit-to-mill/<int:mill_id>/", Add_unit_to_mill, name="add_unit_to_mill"),
    path('mills-list/', mills_list, name='mills_list'),



    #Others
    path("add-inspector/", add_inspector, name="add_inspector"),
    # path("assign-unit-to-me-inspector/<int:unit_id>/<int:insp_id>/", assign_unit_to_me_inspector, name="assign_unit_to_me_inspector"),
    path("assign-inspector/<int:unit_id>/", assign_inspector, name="assign_inspector"),
    path("inspection-reports_add/<int:mill_id>/<int:unit_id>/", add_inspection_report, name="add_inspection_report"),
    path("inspection-reports/", view_inspection_reports, name="view_inspection_reports"),
    path("list-inspectors/", list_inspectors, name="list_inspectors"),


    #master_adm
    path('master-settings/', master_settings_view, name='master_settings'), 
    path('view-fbr-oficials/', view_fbr_oficials, name='view_fbr_oficials'),
    path("add-fbr-oficials/", add_fbr_oficials, name="add_fbr_oficials"),


    #Locations
    path('locations/',  view_locations, name='view_locations'),
    path('api/mills-data/',  mills_data_api, name='mills-data-api'),


    #Payments  FBR
    path('list-fbr-payment-accounts/',  list_fbr_payment_accounts, name='list_fbr_payment_accounts'),
    path('add-fbr-paym-acc/',  add_fbr_payment_account, name='add_fbr_paym_acc'),

    #Payment  attachments
    path('add-payment-record/<int:mill_id>/<int:unit_id>/',  add_payment_record, name='add_payment_record'),
    path('add-payment-record-to-invoice/<int:invoice_id>/',  add_payment_record_to_invoice, name='add_payment_record_to_invoice'),
    path("payment-records/", payment_records_list, name="payment_records"),

     
    #Payment  inspection    
    path('inspect-payment/<int:payment_id>/', inspect_payment, name='inspect_payment'),
    path('view-inspection-of-payment/<int:payment_id>/', view_inspection_of_payment, name='view_inspection_of_payment'),



    #Emails
    path("set-password/<int:uid>/<str:token>/", set_password_view, name="set_password"),


    # UsersLoginLogoutActivitiesLog
    path("log-n-out-act-logs/",  view_users_login_logout_activities_log, name="users_login_logout_activities_log"),


    #Invoices
    path('invoice/create/<int:unit_id>/', create_invoice, name='create_invoice'),
    path('invoice/<int:invoice_id>/pdf/', generate_invoice_pdf, name='generate_invoice_pdf'),
    path("invoices-records/", Invoices_records_list, name="invoices_records"),
    path('analyze-invoice-payment/<int:invoice_id>/', analyze_invoice_payment, name='analyze_invoice_payment'),


    #Chats
    path("users/",  Chat_user_list, name="Chat_user_list"),
    path("chat/<str:username>/", chat_room, name="the_chat_room"),

]