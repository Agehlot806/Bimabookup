from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404,render
from django.shortcuts import redirect,render
from django.contrib import messages
from django.views import View
from .models import *
from .forms import *


def get_id_from_session(request):
    id=request.session['id']
    return id
def Index(request):
     return render(request, 'index.html')


# DashBoardView
def dashboard(request):
    agentcount=Agents.objects.filter(profile_id=get_id_from_session(request)).count()
    staffcount=StaffModel.objects.filter(profile_id=get_id_from_session(request)).count()
    spcount=ServiceProvider.objects.filter(profile_id=get_id_from_session(request)).count()
    policycount=Agents.objects.filter(profile_id=get_id_from_session(request)).count()
    print('total agents are:',agentcount)
    return render(request,'dashboard.html',{'agentcount':agentcount,'staffcount':staffcount,'spcount':spcount,'totalpolicy':policycount})


#LoginView
def login_form(request):
    return render(request,'login.html')
def loginView(request):
    try:
        if request.method=='POST':
            full_name = request.POST['full_name']
            password = request.POST['password']
            user=ProfileModel.objects.filter(full_name=full_name,password=password).first()
            user1=Agents.objects.filter(login_id=full_name,password=password).first()
            user2=StaffModel.objects.filter(login_id =full_name,password=password).first()
            if user:
                p=ProfileModel.objects.filter(full_name=full_name,password=password).first()
                id = p.id
                request.session['id']=user.id
                request.session['full_name']=user.full_name
                userr_ob = UserRole.objects.filter(profile_id=id)
                if userr_ob:
                    pass
                else:
                    UserRole.objects.create(profile_id_id = id, role='admin')
                return redirect('bima_policy:dashboard')
            if user1:
                id = request.session['id']=user1.login_id
                request.session['full_name']=user1.full_name
                # user_ob = UserRole.objects.filter(agent_id=id).first()
                # role = user_ob.role
                request.session["role"] = "agent"
                return redirect('bima_policy:dashboard')
            if user2:
                request.session['id']=user2.login_id
                request.session['staffname']=user2.staffname
                request.session["role"] = "staff"
                return redirect('bima_policy:dashboard')
            return render(request,'login.html',{'error_message':'Invalid ID or Password!'})
    except (ProfileModel.DoesNotExist,Agents.DoesNotExist,StaffModel.DoesNotExist):
        error_message='Invalid ID or Password!'
        return render(request,'login.html',{'error_message':error_message})


# ProfileView
def Profile(request):
    if request.method=="GET":
        try:
            data = ProfileModel.objects.filter(id=get_id_from_session(request))
            return render(request, 'profile/profile.html',{'data':data})
        except ProfileModel.DoesNotExist:
            return HttpResponse('Profile does not exist.')
    elif request.method=='POST' and 'updpassword' in request.POST:
        try:
            profile=ProfileModel.objects.filter(id=get_id_from_session(request))
            password=request.POST['password']
            profile.update(password=password)
            return render(request,'login.html',{'success_message':'Password update successfully!'})
        except ProfileModel.DoesNotExist:
            return HttpResponse('Profile does not exist.')



# UserView
def staffmanage(request):
    if request.method=='GET':
        try:
            data = StaffModel.objects.filter(profile_id=get_id_from_session(request))
            return render(request, 'user/user.html',{'data':data})
        except StaffModel.DoesNotExist:
            return render(request, 'user/user.html')
    else:
        if 'staff_add' in request.POST:
            data = ProfileModel.objects.get(id=get_id_from_session(request))
            staffname=request.POST['staffname']
            password=request.POST['password']
            StaffModel.objects.create(staffname=staffname,password=password,profile_id=data)
            return HttpResponseRedirect(request.path,('staff'))

def staff_edit(request,id):
    if request.method=='GET':
        try:
            data = StaffModel.objects.filter(login_id=id)
            return render(request, 'user/user_edit.html',{'data':data})
        except StaffModel.DoesNotExist:
            return render(request, 'user/user_edit.html')
    else:
        if 'profile' in request.POST:
            StaffModel.objects.filter(login_id=id).update(staffname=request.POST['full_name'],status=request.POST['status'])
        return redirect('bima_policy:staff')


# ProfileView
def bank_details(request):
    if request.method=="GET":
        try:
            data={}
            pdata = ProfileModel.objects.filter(id=get_id_from_session(request))
            bdata = BankDetail.objects.filter(profile_id_id=get_id_from_session(request))
            return render(request, 'profile/bank_details.html' , {'pdata':pdata,'bdata':bdata})
        except BankDetail.DoesNotExist:
            return render(request, 'profile/bank_details.html')
    else:
        try:
            if "bankadd" in request.POST:
                data = ProfileModel.objects.get(id=get_id_from_session(request))
                beneficiary_name=request.POST['beneficiary_name']
                acc_no=request.POST['account_number']
                bank_name=request.POST['bank_name']
                BankDetail.objects.create(beneficiary_name=beneficiary_name, acc_no=acc_no,bank_name=bank_name, profile_id=data)
                return HttpResponseRedirect(request.path,('bank_det'))
        except ProfileModel.DoesNotExist:
            return HttpResponse('error')
    return HttpResponseRedirect(request.path,('bank_det'))  

def delete_bank_details(request,id):
    if request.method=="GET":
        return redirect('bima_policy:bank_det')
    else:
        if "delete" in request.POST:
            # obj=BankDetail.objects.filter(id=id)
            #obj.delete()
            get_object_or_404(BankDetail, id=id).delete()
            return redirect('bima_policy:bank_det')

def change_password(request):
    if request.method=='POST' and 'updpassword' in request.POST:
        profile=ProfileModel.objects.filter(id=get_id_from_session(request))
        password=request.POST['password']
        profile.update(password=password)


# RTOView
def rto_list(request):
    if request.method=="GET":
        data=RtoConversionModel.objects.filter(profile_id_id=get_id_from_session(request))
        return render(request, 'rto/RTO.html', {'data': data})
    if request.method=="POST" and 'rto_add' in request.POST:
        data = ProfileModel.objects.get(id=get_id_from_session(request))
        rtoseries=request.POST['rtoseries']
        rtoreturn=request.POST['rtoreturn']
        RtoConversionModel.objects.create(rto_series=rtoseries,rto_return=rtoreturn,profile_id=data)
        return redirect('bima_policy:rto')

def update_rto(request,id):
    data={}
    if request.method=="GET":
        data = RtoConversionModel.objects.filter(profile_id_id=get_id_from_session(request))
        udata=RtoConversionModel.objects.filter(id=id)
        return render(request, 'RTO.html',{'data':data,'udata':udata})
    if request.method=='POST':
        if "delete" in request.POST:
            item = get_object_or_404(RtoConversionModel, id=id)
            item.delete()
            return redirect('bima_policy:rto')


# InsuranceView
def ins_comp(request):
    if request.method=="GET":
        try:
            data=InsuranceCompany.objects.filter(profile_id=get_id_from_session(request))
            return render(request,'insurancecompany/insurance_comp.html', {'data':data})
        except ProfileModel.DoesNotExist:
            return render(request,'insurancecompany/insurance_comp.html')
    elif 'company_add' in request.POST:
        try:
            data=ProfileModel.objects.get(id=get_id_from_session(request))
            ins_name=request.POST['inscomp_name']
            status=request.POST['status']
            InsuranceCompany.objects.create(comp_name=ins_name,status=status,profile_id=data)
            return redirect('bima_policy:ins_comp')
        except ProfileModel.DoesNotExist:
            return HttpResponseRedirect(request.path,('bank_det'))

def ins_del(request,id):
    if request.method=='POST' and 'delete' in request.POST:
        data=InsuranceCompany.objects.filter(id=id)
        data.delete()
        return redirect('bima_policy:ins_comp')


# VehicleView
def vehicle_view(request):
    if request.method=="GET":
        try:
            data=VehicleMakeBy.objects.filter(profile_id_id=get_id_from_session(request))
            datamn=VehicleModelName.objects.filter(profile_id_id=get_id_from_session(request))
            datavc=VehicleCategory.objects.filter(profile_id_id=get_id_from_session(request))
            mylist=zip(datamn,data)
            return render(request,'vehicle/vehicle.html',{'list':mylist, 'datavc':datavc, 'data':data,'datamn':datamn})
        except(VehicleMakeBy.DoesNotExist,VehicleModelName.DoesNotExist,VehicleCategory.DoesNotExist):
            return render(request,'vehicle/vehicle.html')
    else:
        p= ProfileModel.objects.get(id=get_id_from_session(request))
        if 'mb_add' in request.POST:
            VehicleMakeBy.objects.create(company=request.POST['makeby'],status = request.POST['mbstatus'],profile_id=p)
            return redirect('bima_policy:vehi')
        elif 'vm_add' in request.POST:
            VehicleModelName.objects.create(model=request.POST['model'],status = request.POST['vmstatus'],profile_id=p)
            return redirect('bima_policy:vehi')
        elif 'vc_add' in request.POST:
            VehicleCategory.objects.create(category=request.POST['category'],status = request.POST['vcstatus'],profile_id=p)
            return redirect('bima_policy:vehi')
        return redirect('bima_policy:vehi')

def delete_vehicle(request,id):
    if request.method=="POST" and 'delete' in request.POST:
        data1=VehicleCategory.objects.filter(id=id)
        data2=VehicleMakeBy.objects.filter(id=id)
        data3=VehicleModelName.objects.filter(id=id)
        if data1:
            data1.delete()
        elif data2:
            data2.delete()
        elif data3:
            data3.delete()
        return redirect('bima_policy:vehi')
    elif request.method=="POST" and 'edit' in request.POST:
        return edit_vehicle(request,id)

def edit_vehicle(request,id):
    vcd=VehicleCategory.objects.filter(id=id)
    vmbd=VehicleMakeBy.objects.filter(id=id)
    vmd=VehicleModelName.objects.filter(id=id)
    if request.method=="GET" :
        if vcd:
            data=VehicleCategory.objects.filter(id=id)
            return render(request,'vehicle/vehicle_edit.html',{'data':data})
        elif vmbd:
            data=VehicleMakeBy.objects.filter(id=id)
            return render(request,'vehicle/vmb_edit.html',{'data':data})
        elif vmd:
            data1=VehicleModelName.objects.filter(id=id)
            data=VehicleMakeBy.objects.filter(profile_id=get_id_from_session(request))
            return render(request,'vehicle/vm_edit.html',{'data':data,'data1':data1})
        
    if request.method=='POST':
        if 'vc_update' in request.POST:
            category=request.POST['category']
            status_update=request.POST['status_update']
            VehicleCategory.objects.filter(id=id).update(category=category,status=status_update)
            return redirect('bima_policy:vehi')
        if 'vmb_update' in request.POST:
            company=request.POST['company']
            status_update=request.POST['status_update']
            VehicleMakeBy.objects.filter(id=id).update(company=company,status=status_update)
            return redirect('bima_policy:vehi')
        if 'vm_update' in request.POST:
            company=request.POST.get('company')
            model=request.POST['model']
            status_update=request.POST['status_update']
            VehicleModelName.objects.filter(id=id).update(company=company,model=model,status=status_update)
            return redirect('bima_policy:vehi')


# ServiceProviderView
def service_provider(request):
    if request.method=="GET":
        try:
            brokerdata = BrokerCode.objects.filter(profile_id = get_id_from_session(request))
            data = ServiceProvider.objects.filter(profile_id = get_id_from_session(request))
            return render(request,'serviceprovider/service_provider.html',{'data':data, 'brokerdata':brokerdata})  
        except (ServiceProvider.DoesNotExist , BrokerCode.DoesNotExist):
            return render(request,'serviceprovider/service_provider.html') 
    else:
        if 'code_add' in request.POST: 
            data =ProfileModel.objects.get(id = get_id_from_session(request))
            code=request.POST['code']
            status=request.POST['status']
            BrokerCode.objects.create(code=code,status=status,profile_id=data)
            return redirect('bima_policy:service_p')
def del_broker_code(request,id):
    BrokerCode.objects.filter(id=id).delete()
    return redirect('bima_policy:service_p')

def add_sp(request):
    if request.method=="GET":
        data =ServiceProvider.objects.filter(profile_id=get_id_from_session(request))
        return render(request,'serviceprovider/add_sp.html', {'data':data})
    else:
       if 'subbtn' in request.POST: 
            p=ProfileModel.objects.get(id=get_id_from_session(request))
            data =ServiceProvider.objects.filter(profile_id_id=get_id_from_session(request))
            full_name=request.POST['full_name']
            email_id=request.POST['email_id']
            phone=request.POST['phone']
            address=request.POST['address']
            state=request.POST['state']
            city=request.POST['city']
            gstin=request.POST['gstin']
            pan=request.POST['pan']
            ServiceProvider.objects.create(full_name=full_name, email_id=email_id, mob_no=phone, address=address, state= state, city=city, GSTIN=gstin,PAN=pan,profile_id=p)
            return redirect('bima_policy:service_p')

def delete_sp(request,id):
    if request.method=='POST':
        ServiceProvider.objects.get(id=id).delete()
        return redirect('bima_policy:service_p')

def edit_sp(request,id):
    if request.method=='GET': 
        data=ServiceProvider.objects.filter(id=id)
        return render(request,'serviceprovider/edit_sp.html',{'data':data})
    elif request.method=='POST' and 'subbtn' in request.POST:
        # pd=ProfileModel.objects.get(id=get_id_from_session(request))
        data =ServiceProvider.objects.filter(id=id)
        full_name=request.POST['full_name']
        email_id=request.POST['email_id']
        phone=request.POST['phone']
        address=request.POST['address']
        state=request.POST['state']
        city=request.POST['city']
        gstin=request.POST['gstin']
        pan=request.POST['pan']
        data.update(full_name=full_name, email_id=email_id, mob_no=phone, address=address, state= state, city=city, GSTIN=gstin,PAN=pan)
        return redirect('bima_policy:service_p')
    return redirect('bima_policy:service_p')


#PolicyView
class create_policy(View):
    def get(self,request):
        data=InsuranceCompany.objects.filter(profile_id=get_id_from_session(request))
        datasp=ServiceProvider.objects.filter(profile_id=get_id_from_session(request))
        databc=BrokerCode.objects.filter(profile_id=get_id_from_session(request))
        datamb=VehicleMakeBy.objects.filter(profile_id=get_id_from_session(request))
        datavm=VehicleModelName.objects.filter(profile_id=get_id_from_session(request))
        datavc=VehicleCategory.objects.filter(profile_id=get_id_from_session(request))
        datag=Agents.objects.filter(profile_id=get_id_from_session(request))
        return render(request,'policylist/policy_list.html',{'data':data,'datasp':datasp,'databc':databc,'datamb':datamb, 'datavm':datavm, 'datavc':datavc,'datag':datag})
    def post(self,request):
        p=ProfileModel.objects.get(id=get_id_from_session(request))
        policy_no=request.POST['policy_no']
        registration=request.POST['registration']
        case_type=request.POST['case_type']
        ins_company=request.POST['ins_company']
        service_provider=request.POST['service_provider']
        code=request.POST['code']
        issue_date=request.POST['issue_date']
        risk_date=request.POST['risk_date']
        cpa=request.POST['cpa']
        document=request.FILES['document']
        fs=FileSystemStorage()
        fs.save(document.name, document)
        previous_policy=request.FILES.get('previous_policy')
        vehicle_rc=request.FILES.get('vehicle_rc')
        fs1=FileSystemStorage()
        fs2=FileSystemStorage()
        if previous_policy is not None:
            fs1.save(previous_policy.name, previous_policy)
        if vehicle_rc is not None:
            fs2.save(vehicle_rc.name, vehicle_rc)
        vehicle_makeby=request.POST['vehicle_makeby']
        vehicle_model=request.POST['vehicle_model']
        vehicle_category=request.POST['vehicle_category']
        vehicle_other_info=request.POST['vehicle_other_info']
        fuel_type=request.POST['fuel_type']
        manu_year=request.POST['manu_year']
        engine_no=request.POST['engine_no']
        chasis_no=request.POST['chasis_no']
        agent=request.POST['agent']
        cust_name=request.POST['cust_name']
        remarks=request.POST['remarks']
        od=request.POST['od']
        tp=request.POST['tp']
        gst=request.POST['gst']
        net=request.POST['total']
        payment_mode=request.POST['payment_mode']
        total=request.POST['total']
        policy_type=request.POST.get('policy_type')
        Policy.objects.create(policy_no=policy_no, registration_no=registration, casetype=case_type, insurance_comp=ins_company, sp_name=service_provider, sp_brokercode=code, issueDate=issue_date,riskDate=risk_date,
        CPA=cpa,insurance=document, previous_policy=previous_policy,vehicle_rc=vehicle_rc,vehicle_makeby=vehicle_makeby,vehicle_model=vehicle_model, vehicle_category=vehicle_category,other_info=vehicle_other_info,
        vehicle_fuel_type=fuel_type,manufature_year=manu_year,engine_no= engine_no,chasis_no=chasis_no,agent_name=agent,customer_name=cust_name,remark=remarks,OD_premium=od,
        TP_premium=tp,GST=gst,net=net,payment_mode=payment_mode,total=total,policy_type=policy_type,profile_id=p)
        return HttpResponseRedirect(request.path,('policy_list'))

def policy_entry(request):
    data = Policy.objects.filter(profile_id=get_id_from_session(request)).order_by('-policyid').values()
    datag=Agents.objects.filter(profile_id=get_id_from_session(request))
    return render(request, 'policylist/policy_entry_list.html',{'data':data ,'datag':datag})

def edit_policy(request,id):
    if request.method=="GET":
        data=Policy.objects.filter(policyid=id)
        datai=InsuranceCompany.objects.filter(profile_id=get_id_from_session(request))
        datasp=ServiceProvider.objects.filter(profile_id=get_id_from_session(request))
        databc=BrokerCode.objects.filter(profile_id=get_id_from_session(request))
        datamb=VehicleMakeBy.objects.filter(profile_id=get_id_from_session(request))
        datavm=VehicleModelName.objects.filter(profile_id=get_id_from_session(request))
        datavc=VehicleCategory.objects.filter(profile_id=get_id_from_session(request))
        datag=Agents.objects.filter(profile_id=get_id_from_session(request))
        return render(request,'policylist/edit_policy.html',{'data':data,'datasp':datasp,'databc':databc,'datamb':datamb, 'datavm':datavm, 'datavc':datavc,'datag':datag,'datai':datai})
    else:
        policy_no=request.POST['policy_no']
        registration=request.POST['registration']
        case_type=request.POST['case_type']
        ins_company=request.POST['ins_company']
        service_provider=request.POST['service_provider']
        code=request.POST['code']
        issue_date=request.POST['issue_date']
        risk_date=request.POST['risk_date']
        cpa=request.POST['cpa']
        document=request.FILES['document']
        fs=FileSystemStorage()
        fs.save(document.name, document)
        previous_policy=request.FILES.get('previous_policy')
        fs1=FileSystemStorage()
        if previous_policy is not None:
            fs1.save(previous_policy.name, previous_policy)
        vehicle_rc=request.FILES.get('vehicle_rc')
        fs2=FileSystemStorage()
        if vehicle_rc is not None:
            fs2.save(vehicle_rc.name, vehicle_rc)
        vehicle_makeby=request.POST['vehicle_makeby']
        vehicle_model=request.POST['vehicle_model']
        vehicle_category=request.POST['vehicle_category']
        vehicle_other_info=request.POST['vehicle_other_info']
        fuel_type=request.POST['fuel_type']
        manu_year=request.POST['manu_year']
        engine_no=request.POST['engine_no']
        chasis_no=request.POST['chasis_no']
        agent=request.POST['agent']
        cust_name=request.POST['cust_name']
        remarks=request.POST['remarks']
        od=request.POST['od']
        tp=request.POST['tp']
        gst=request.POST['gst']
        net=request.POST['total']
        payment_mode=request.POST['payment_mode']
        total=request.POST['total']
        policy_type=request.POST.get('policy_type')
        Policy.objects.filter(policyid=id).update(policy_no=policy_no, registration_no=registration, casetype=case_type, insurance_comp=ins_company, sp_name=service_provider, sp_brokercode=code, issueDate=issue_date,riskDate=risk_date,CPA=cpa,insurance=document, previous_policy=previous_policy,vehicle_rc=vehicle_rc,vehicle_makeby=vehicle_makeby,vehicle_model=vehicle_model, vehicle_category=vehicle_category,other_info=vehicle_other_info,vehicle_fuel_type=fuel_type,manufature_year=manu_year,engine_no= engine_no,chasis_no=chasis_no,agent_name=agent,customer_name=cust_name,remark=remarks,OD_premium=od,TP_premium=tp,GST=gst,net=net,payment_mode=payment_mode,total=total,policy_type=policy_type)
        return redirect('bima_policy:policy_entry')


def policy_delete(request,id):
    if request.method=='GET':
        Policy.objects.get(policyid=id).delete()
        return redirect('bima_policy:policy_entry')



def logout(request):
    request.session.clear()
    return render(request,'login.html')




def agent(request):
    data = Agents.objects.filter(profile_id=get_id_from_session(request))
    return render(request, 'agents/agent.html', {'data':data})



def add_agent(request):
    try:
        if request.method=="GET":
            Adata=Slab.objects.filter(profile_id=get_id_from_session(request))
            data =Agents.objects.filter(profile_id=get_id_from_session(request))
            
            return render(request,'agents/add_agent.html', {'data':data,'Adata':Adata})
    except Agents.DoesNotExist:
        return render(request, 'agents/add_agent.html')
    else:
        if 'subagent' in request.POST: 
            data =ProfileModel.objects.get(id=get_id_from_session(request))
            full_name=request.POST['full_name']
            email_id=request.POST['email_id']
            phone=request.POST['phone']
            address=request.POST['address']
            state=request.POST['state']
            city=request.POST['city']
            agent_slab=request.POST['agent_slab']
            gstin=request.POST['gstin']
            pan=request.POST['pan']
            docs=request.POST.get('docs')
            password=request.POST['password']
            # a=Agents.objects.get(full_name=full_name)
            # if full_name==Agents.objects.get(full_name=a.full_name):
            #     error_message="Full Name already exist! Please enter unique name to continue..."
            #     return redirect('bima_policy:add_agent',{'error_message':error_message})
            # else:
            Agents.objects.create(full_name=full_name, email_id=email_id, mob_no=phone, address=address, state= state, city=city,slab=agent_slab, GSTIN=gstin,PAN=pan,document=docs,password=password ,profile_id=data)
            return redirect('bima_policy:agent')









# PayoutView
def slab(request):
    if request.method=="GET":
        try:
            data =Slab.objects.filter(profile_id=get_id_from_session(request))
            return render(request,'payout/slab.html', {'data':data})
        except Slab.DoesNotExist:
            return render(request,'payout/slab.html')
    else :
        try:
            if 'slab_add' in request.POST:
                profile=ProfileModel.objects.get(id=get_id_from_session(request))
                slab_name=request.POST['slab']
                Slab.objects.create(slab_name=slab_name,profile_id=profile)
                return redirect('bima_policy:slab')
            # if 'slab_remove' in request.POST:

        except ProfileModel.DoesNotExist:
            return redirect('bima_policy:slab')

def slab_delete(request,id):
    data=Slab.objects.filter(slab_name=id)
    data.delete()
    return redirect('bima_policy:slab')

def slab_edit(request,id):
    data=Slab.objects.filter(slab_name=id)
    if request.method=='GET':
        return render(request,'payout/payoutname_edit.html',{'data':data})
    else:
        slab_name=request.POST['slab_name']
        status=request.POST['status']
        Slab.objects.filter(slab_name=id).update(slab_name=slab_name,status=status)
        return redirect('bima_policy:slab') 

def slab_payout(request,id):
    if request.method=='GET':
        try:
            data=Payout.objects.filter(profile_id=get_id_from_session(request))
            data1=data.filter(slab_name=id)
            return render(request,'payout/slab_payoutlist.html', {'data1':data1})
        except Payout.DoesNotExist:
            return render(request,'payout/slab_payoutlist.html')


def slab_payoutform(request):
    if request.method=="GET":
        pol_provider=ServiceProvider.objects.filter(profile_id=get_id_from_session(request))
        ins_comp=InsuranceCompany.objects.filter(profile_id=get_id_from_session(request))
        vcat=VehicleCategory.objects.filter(profile_id=get_id_from_session(request))
        vmb=VehicleMakeBy.objects.filter(profile_id=get_id_from_session(request))
        vmodel=VehicleModelName.objects.filter(profile_id=get_id_from_session(request))
        slab = Slab.objects.filter(profile_id=get_id_from_session(request))
        return render(request,'payout/slab_payoutform.html', {'slab': slab,'vcat':vcat,'vmb':vmb,'vmodel':vmodel,'ins_comp':ins_comp,'pol_provider':pol_provider})

    if request.method=='POST' and 'savepayout' in request.POST:
        data=ProfileModel.objects.get(id=get_id_from_session(request))
        payoutName=request.POST['payout_name']
        slab=request.POST['slab']
        s=Slab.objects.get(slab_name=slab)
        status=request.POST['status']
        vehicle_category=request.POST['vehicle_category']
        Insurance_company=request.POST['ins_com']
        policy_provider=request.POST['policy_provider']
        vehicle_make_by=request.POST['vehicle_make_by']
        rtos=request.POST['rtos']
        casetype=request.POST['casetype']
        coverage=request.POST['coverage']
        fueltype=request.POST['fueltype']
        cpa=request.POST['cpa']
        rewards_on=request.POST['areward_on']
        rewards_age=request.POST['areward_pct']
        self_rewards_on=request.POST['sreward_on']
        self_rewards_age=request.POST['sreward_pct']
        Payout.objects.create(payout_name=payoutName,slab_name=s,status=status,vehicle_category=vehicle_category,Insurance_company=Insurance_company,policy_provider=policy_provider,vehicle_make_by=vehicle_make_by,rto=rtos,case_type=casetype,coverage=coverage,fuel_type=fueltype,cpa=cpa,rewards_on=rewards_on,rewards_age=rewards_age,self_rewards_on=self_rewards_on,self_rewards_age=self_rewards_age,profile_id=data)
        return redirect('bima_policy:slab')

def payout_delete(request,id):
    Payout.objects.filter(payoutid=id).delete()
    return redirect('bima_policy:slab')

def payout_edit(request,id):
    data=Payout.objects.filter(payoutid=id)
    if request.method=="GET":
        pol_provider=ServiceProvider.objects.filter(profile_id=get_id_from_session(request))
        ins_comp=InsuranceCompany.objects.filter(profile_id=get_id_from_session(request))
        vcat=VehicleCategory.objects.filter(profile_id=get_id_from_session(request))
        vmb=VehicleMakeBy.objects.filter(profile_id=get_id_from_session(request))
        vmodel=VehicleModelName.objects.filter(profile_id=get_id_from_session(request))
        slab = Slab.objects.filter(profile_id=get_id_from_session(request))
        return render(request,'payout/edit_payoutform.html', {'slab': slab,'vcat':vcat,'vmb':vmb,'vmodel':vmodel,'ins_comp':ins_comp,'pol_provider':pol_provider,'data':data})

    if request.method=='POST':
        payoutName=request.POST['payout_name']
        slab=request.POST['slab']
        s=Slab.objects.get(slab_name=slab)
        status=request.POST['status']
        vehicle_category=request.POST['vehicle_category']
        Insurance_company=request.POST['ins_com']
        policy_provider=request.POST['policy_provider']
        vehicle_make_by=request.POST['vehicle_make_by']
        rtos=request.POST['rtos']
        casetype=request.POST['casetype']
        coverage=request.POST['coverage']
        fueltype=request.POST['fueltype']
        cpa=request.POST['cpa']
        rewards_on=request.POST['areward_on']
        rewards_age=request.POST['areward_pct']
        self_rewards_on=request.POST['sreward_on']
        self_rewards_age=request.POST['sreward_pct']
        Payout.objects.filter(payoutid=id).update(payout_name=payoutName,slab_name=s,status=status,vehicle_category=vehicle_category,Insurance_company=Insurance_company,policy_provider=policy_provider,vehicle_make_by=vehicle_make_by,rto=rtos,case_type=casetype,coverage=coverage,fuel_type=fueltype,cpa=cpa,rewards_on=rewards_on,rewards_age=rewards_age,self_rewards_on=self_rewards_on,self_rewards_age=self_rewards_age)
        return redirect('bima_policy:slab_payout')

def policy_import(request):
    if request.method=='GET':
        return render(request,'policylist/policy_list_import.html')
    else:
        if 'submitup' in request.POST:
            fcsv=request.FILES.get('fcsv')
            fs=FileSystemStorage()
            fs.save(fcsv.name, fcsv)
            InsuranceUpload.objects.create(ins_upload=fcsv)
            messages.success(request, 'Insurance upload succefully......')
            return HttpResponseRedirect(request.path,('policy_list/policy_list_import'))


def upcoming_renewal(request):
    return render(request, 'upcomingrenewal/upcoming_renewal.html')


def agentpayable(request):
    agent_obj = Agents.objects.filter(profile_id=get_id_from_session(request))
    policy_data= []
    grand_total_policy = []
    for agent in agent_obj:
        agent_name = agent.full_name
        policy_obj = Policy.objects.filter(agent_name=agent_name)
        total_policy = 0
        issueDate = ""
        for policy in policy_obj:
            total_policy = total_policy + 1
            # issueDate =policy.issueDate
            if policy_obj:
                issueDate = policy.issueDate
            else:
                issueDate = ""
        data ={
            "issueDate":issueDate,
            "agent_name":agent_name,
            "total_policy":total_policy,
            "ok_policy":total_policy
        }
        policy_data.append(data)
        grand_total_policy.append(total_policy)
    grand_policy = sum(grand_total_policy)
    return render(request, 'ledger/agent_payable.html',{'data':policy_data, 'datas':agent_obj, 'grand_policy':grand_policy})


def agent_statement(request):
    return render(request, 'ledger/agent_statement.html')




def sp_receivable(request):
    agent_obj = ServiceProvider.objects.filter(profile_id=get_id_from_session(request))
    policy_data= []
    grand_total_policy = []
    for agent in agent_obj:
        agent_name = agent.full_name
        policy_obj = Policy.objects.filter(sp_name=agent_name)
        total_policy = 0
        for policy in policy_obj:
            total_policy = total_policy + 1
            # issueDate =policy.issueDate
            if policy_obj:
                issueDate = policy.issueDate
            else:
                issueDate = ""
        data = {
            "issueDate":issueDate,
            "agent_name":agent_name,
            "total_policy":total_policy,
            "ok_policy":total_policy
        }
        policy_data.append(data)
        grand_total_policy.append(total_policy)
    grand_policy = sum(grand_total_policy)
    print(grand_policy)
    return render(request, 'ledger/SP_recevaible.html' ,{'data':policy_data, 'datas':agent_obj, 'grand_policy':grand_policy})


def sp_statement(request):
    return render(request, 'ledger/SP_statement.html')




def report_agent(request):
    agent_obj = Agents.objects.filter(profile_id=get_id_from_session(request))
    policy_data= []
    total_count_policy = []
    total_od = []
    total_tp= []
    total_net = []
    for agent in agent_obj:
        agent_name = agent.full_name
        policy_obj = Policy.objects.filter(agent_name=agent_name)
        count_policy = 0
        for policy in policy_obj:
            count_policy = count_policy + 1
            # total_count_policy.append(count_policy)
            OD_premium = policy.OD_premium
            # total_od.append(OD_premium)
            TP_premium = policy.TP_premium
            # total_tp.append(TP_premium)
            nett = policy.net
            # total_net.append(nett)
        data = {
            "count_policy":count_policy,
            "agent_name":agent_name,
            "OD_premium":OD_premium,
            "TP_premium":TP_premium,
            "net":nett,
        }
        policy_data.append(data)
        total_count_policy.append(count_policy)
        total_od.append(OD_premium)
        total_tp.append(TP_premium)
        total_net.append(nett)
    total_od = sum(total_od)
    total_tp = sum(total_tp)
    total_net = sum(total_net)
    total_count_policy = sum(total_count_policy)
    return render(request, 'reports/report_agent.html' ,{"datas":policy_data,"total_count_policy":total_count_policy, "total_od":total_od , "total_tp":total_tp,"total_net":total_net})


def report_policyprovider(request):
    agent_obj = ServiceProvider.objects.filter(profile_id=get_id_from_session(request))
    policy_data= []
    total_count_policy = []
    total_od = []
    total_tp= []
    total_net = []
    for agent in agent_obj:
        agent_name = agent.full_name
        policy_obj = Policy.objects.filter(sp_name=agent_name)
        count_policy = 0
        for policy in policy_obj:
            count_policy = count_policy + 1
            OD_premium = policy.OD_premium
            TP_premium = policy.TP_premium
            nett = policy.net
            data = {
                "count_policy":count_policy,
                "agent_name":agent_name,
                "OD_premium":OD_premium,
                "TP_premium":TP_premium,
                "net":nett,
            }
            policy_data.append(data)
            total_count_policy.append(count_policy)
            total_od.append(OD_premium)
            total_tp.append(TP_premium)
            total_net.append(nett)
    total_od = sum(total_od)
    total_tp = sum(total_tp)
    total_net = sum(total_net)
    total_count_policy = sum(total_count_policy)
    return render(request,'reports/report_Policyprovider.html' ,{"datas":policy_data,"total_count_policy":total_count_policy, "total_od":total_od , "total_tp":total_tp, "total_net":total_net})
    
def report_vehicleCategory(request):
    agent_obj = VehicleCategory.objects.filter(profile_id=get_id_from_session(request))
    policy_data= []
    total_count_policy = []
    total_od = []
    total_tp= []
    total_net = []
    for agent in agent_obj:
        vc = agent.category
        policy_obj = Policy.objects.filter(vehicle_category=vc)
        count_policy = 0
        OD = 0
        TP = 0
        nett = 0
        for policy in policy_obj:
            count_policy = count_policy + 1
            # total_count_policy.append(count_policy)
            OD = policy.OD_premium
            # total_od.append(OD_premium)
            TP= policy.TP_premium
            # total_tp.append(TP_premium)
            nett = policy.net
            # total_net.append(nett)
        data = {
            "count_policy":count_policy,
            "agent_name":vc,
            "OD_premium":OD,
            "TP_premium":TP,
            "net":nett,
        }
        policy_data.append(data)
        total_count_policy.append(count_policy)
        total_od.append(OD)
        total_tp.append(TP)
        total_net.append(nett)
    total_od = sum(total_od)
    total_tp = sum(total_tp)
    total_net = sum(total_net)
    total_count_policy = sum(total_count_policy)
    return render(request, 'reports/report_vehicalCategory.html' ,{"datas":policy_data,"total_count_policy":total_count_policy, "total_od":total_od , "total_tp":total_tp, "total_net":total_net })
def report_brokercode(request):
    agent_obj = BrokerCode.objects.filter(profile_id=get_id_from_session(request))
    policy_data= []
    total_count_policy = []
    total_od = []
    total_tp= []
    total_net = []
    for agent in agent_obj:
        broker = agent.code
        policy_obj = Policy.objects.filter(sp_brokercode=broker)
        count_policy = 0
        OD = 0
        TP = 0
        nett = 0
        for policy in policy_obj:
            count_policy = count_policy + 1
            # total_count_policy.append(count_policy)
            OD = policy.OD_premium
            # total_od.append(OD_premium)
            TP= policy.TP_premium
            # total_tp.append(TP_premium)
            nett = policy.net
            # total_net.append(nett)
        data = {
            "count_policy":count_policy,
            "agent_name":broker,
            "OD_premium":OD,
            "TP_premium":TP,
            "net":nett,
        }
        policy_data.append(data)
        total_count_policy.append(count_policy)
        total_od.append(OD)
        total_tp.append(TP)
        total_net.append(nett)
    total_od = sum(total_od)
    total_tp = sum(total_tp)
    total_net = sum(total_net)
    total_count_policy = sum(total_count_policy)
    return render(request, 'reports/report_brokerCode.html' ,{"datas":policy_data,"total_count_policy":total_count_policy, "total_od":total_od , "total_tp":total_tp, "total_net":total_net })
def report_insurance_comp(request):
    agent_obj = InsuranceCompany.objects.filter(profile_id=get_id_from_session(request))
    policy_data= []
    total_count_policy = []
    total_od = []
    total_tp= []
    total_net = []
    for agent in agent_obj:
        inscomp = agent.comp_name
        policy_obj = Policy.objects.filter(insurance_comp=inscomp)
        count_policy = 0
        OD = 0
        TP = 0
        nett = 0
        for policy in policy_obj:
            count_policy = count_policy + 1
            # total_count_policy.append(count_policy)
            OD = policy.OD_premium
            # total_od.append(OD_premium)
            TP= policy.TP_premium
            # total_tp.append(TP_premium)
            nett = policy.net
            # total_net.append(nett)
        data = {
            "count_policy":count_policy,
            "agent_name":inscomp,
            "OD_premium":OD,
            "TP_premium":TP,
            "net":nett,
        }
        policy_data.append(data)
        total_count_policy.append(count_policy)
        total_od.append(OD)
        total_tp.append(TP)
        total_net.append(nett)
    total_od = sum(total_od)
    total_tp = sum(total_tp)
    total_net = sum(total_net)
    total_count_policy = sum(total_count_policy)
    return render(request, 'reports/report_insurance_company.html' ,{"datas":policy_data,"total_count_policy":total_count_policy, "total_od":total_od , "total_tp":total_tp, "total_net":total_net })


def subscription(request):
    return render(request, 'subscription.html')


def agent_profile(request):
    return render(request,'agents/agent_particular.html')

