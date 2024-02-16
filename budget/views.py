from django.shortcuts import render,redirect

# Create your views here.
# :localhost8000/transation/all/

from django.views.generic import View
from budget.models import Transaction
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.cache import never_cache

def signin_required(fn):

    def wrapper(request,*args,**kwargs):
              if not request.user.is_authenticated:
                messages.error(request,"invalid session")
                return redirect("signin")
              else:
                  return fn(request,*args,**kwargs)
    return wrapper

desc=[signin_required,never_cache]


class TransactionForm(forms.ModelForm):
    class Meta:
        model=Transaction
        # fields=["field1","field2"]
        # fields="_all_"
        exclude=("created_date","user_object")
        widgets={
            "title":forms.TextInput(attrs={"class":"form-control"}),
            "amount":forms.NumberInput(attrs={"class":"form-control"}),
            "type":forms.Select(attrs={"class":"form-control form-select"}),
            "category":forms.Select(attrs={"class":"form-control form-select"})
        }


@method_decorator(desc,name="dispatch")
class TransactionListView(View):
    def get(self,request,*args,**kwargs):
        qs=Transaction.objects.filter(user_object=request.user)
        cur_month=timezone.now().month
        cur_year=timezone.now().year
        print(cur_month,cur_year)
        data=Transaction.objects.filter(
            created_date__month=cur_month,
            created_date__year=cur_year,
            user_object=request.user
        ).values("type").annotate(type_sum=Sum("amount"))
        print(data)

        cat_qs=Transaction.objects.filter(
            created_date__month=cur_month,
            created_date__year=cur_year,
            user_object=request.user
        ).values("category").annotate(cat_sum=Sum("amount"))
        print(cat_qs)
        # expense_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="expense",
        #     created_date__month=cur_month,
        #     created_date__year=cur_year
        # ).aaggregate(Sum("amount"))
        # print(expense_total)
        # income_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="income",
        #     created_date__month=cur_month,
        #     created_date__year=cur_year
        # ).aaggregate(Sum("amount"))
        # print(income_total)

        return render(request,"transaction_list.html",{"data":qs,"type_total":data,"cat_total":cat_qs})
    

# view for creating transaction
    # url:localhost8000/transaction/add/
    # methods:get,post



@method_decorator(desc,name="dispatch")    
class TransactionCreateView(View):
    def get(self,request,*args,**kwargs):
        form=TransactionForm()
        return render(request,"transaction_add.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=TransactionForm(request.POST)
        if form.is_valid():
            # form.save()
            data=form.cleaned_data
            Transaction.objects.create(**data,user_object=request.user)
            messages.success(request,"Transaction has been added succesfully")
            return redirect("transaction-list")
        else:
            messages.error(request,"Failed to add transaction")

            return render(request,"transaction_add.html",{"form":form})
        
     # transaction detail view
    # url localhost8000/transaction//
    # method get


@method_decorator(desc,name="dispatch") 
class TransactionDetailView(View):

    def get(self,request,*args,**kwargs):
  
        id=kwargs.get("pk")
        qs=Transaction.objects.get(id=id)
        return render(request,"transaction_detail.html",{"data":qs})
    
    # transation delete View
    # url localhost8000/transaction/1/remove/
    # method get


@method_decorator(desc,name="dispatch")        
class TransactionDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transaction.objects.filter(id=id).delete()
        messages.success(request,"Transaction has been removed")
        return redirect("transaction-list")
    
    # transaction update view
    # url localhost8000/transaction/1/edit/
    # method get,post


@method_decorator(desc,name="dispatch")
class TransactionUpdateView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transaction_object=Transaction.objects.get(id=id)
        form=TransactionForm(instance=Transaction_object)
        return render(request,"transaction_edit.html",{"form":form})
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transaction_object=Transaction.objects.get(id=id)
        data=request.POST
        form=TransactionForm(data,instance=Transaction_object)
        if form.is_valid():
            form.save()
            messages.success(request,"Transaction has been updated successfully")
            return redirect("transaction-list")
        else:
            messages.error(request,"Failed to update transaction")

            return render(request,"transaction_edit.html",{"form":form})
        
class RegistrationForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","email","password",]
        widgets={
            "username":forms.TextInput(attrs={"class":"form-control"}),
            "email":forms.EmailInput(attrs={"class":"form-control"}),
            "password":forms.PasswordInput(attrs={"class":"form-control"})

        
        }


# view for signup
        # url=localhost8000/signup/
class SignUpView(View):
    def get(self,request,*args,**kwargs):
        form=RegistrationForm()
        return render(request,"registration.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(**form.cleaned_data)
            print("account created")
            return redirect("signin")
        else:
            print("failed")
            return render(request,"registration.html",{"form":form})
        
class LoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))
        

# signin view
# url:localhost8000/signin/
# method:get,post
    
class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"signin.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=u_name,password=pwd)
            if user_object:
                login(request,user_object)
                return redirect("transaction-list")
        return render(request,"signin.html",{"form":form})
    

# signout view
# url localhost8000/signout/
# method get

@method_decorator(desc,name="dispatch")
class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")
    


    