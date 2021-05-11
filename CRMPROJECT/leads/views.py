from django.shortcuts import render,redirect,reverse
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView,ListView,DetailView,
                                CreateView,UpdateView,DeleteView,FormView)
from .models import Lead,Agent,Category
from .forms import LeadModelForm,CustomUserCreationForm,AssignAgentForm,LeadCategoryUpdateForm
from agents.mixins import OrganisorAndLoginRequiredMixin


# Create your views here.

class SignUpView(CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse('login')

class LandingPageView(LoginRequiredMixin ,TemplateView):
    template_name = 'leads/landing.html'

class LeadDetailview(LoginRequiredMixin ,DetailView):
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'

    def get_queryset(self):
        user = self.request.user

        # initial qs of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            #filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)  
        return queryset    

class LeadListView(LoginRequiredMixin ,ListView):
    template_name = 'leads/lead_list.html'
    context_object_name = 'leads'

    def get_queryset(self):
        user = self.request.user

        # initial qs of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            #filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)  

        return queryset    

    def get_context_data(self,**kwargs)  :
        context = super(LeadListView, self).get_context_data(**kwargs)  
        user = self.request.user
        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile,
                agent__isnull = True
            )
            context.update({
                "unassigned leads":queryset
            })
        return context    

class LeadCreateView(LoginRequiredMixin ,CreateView):
    template_name = 'leads/lead_create.html'
    form_class = LeadModelForm 

    def get_success_url(self):
        return reverse('leads:lead_list')

    def form_valid(self,form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        send_mail(
            subject='A lead has been created',
            message='Go to the site to see the new lead',
            from_email='test@test.com',
            recipient_list=['test2@test.com']
        )    
        return super(LeadCreateView,self).form_valid(form)

class LeadUpdateView(OrganisorAndLoginRequiredMixin,UpdateView):
    template_name = 'leads/lead_update.html'
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        #initial qs of the organisation
        return Lead.objects.filter(organisation=user.agent.organisation)

    def get_success_url(self):
        return reverse('leads:lead_list')

class LeadDeleteView(OrganisorAndLoginRequiredMixin,DeleteView):
    template_name = 'leads/lead_delete.html'

    def get_queryset(self):
        user = self.request.user
        #initial qs of the organisation
        return Lead.objects.filter(organisation=user.agent.organisation)


    def get_success_url(self):
        return reverse('leads:lead_list')


class AssignAgentView(OrganisorAndLoginRequiredMixin,FormView):
    template_name = 'leads/assign_agent.html'
    form_class = AssignAgentForm

    def get_form_kwargs(self):
        kwargs = super(AssignAgentView,self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request":self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse('leads:lead_list')

    def form_valid(self,form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView,self).form_valid(form) 
        
class CategoryListView(LoginRequiredMixin,ListView):
    template_name = 'leads/category_list.html'
    context_object_name = 'category_list'

    def  get_context_data(self, **kwargs):
        context = super(CategoryListView,self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
        
        context.update({
            "unassigned_lead_count":queryset.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user

        # initial qs of leads for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
            #filter for the agent that is logged in
        return queryset     


class CategoryDetailView(LoginRequiredMixin,DetailView):
    template_name = 'leads/category_list.html'
    context_object_name = 'category'

    """ def get_context_data(self, **kwargs):
        context = super(CategoryDetailView,self).get_context_data(**kwargs)
        leads =  self.get_object().leads.all()
        context.update({
            'leads':leads
       })
        return context"""

    def get_queryset(self):
        user = self.request.user
        # initial qs of leads for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
            #filter for the agent that is logged in
        return queryset     


class LeadCategoryUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'leads/lead_category_update.html'
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user

        # initial qs of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            #filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)  
        return queryset     

    def get_success_url(self):
        return reverse('leads:lead_detail',kwargs={"pk":self.get_object()})



def landing_page(request):
    return render(request,'leads/landing.html')

def lead_list(request):
    leads = Lead.objects.all()
    context = {
        'leads' : leads,
    }
    return render(request,'leads/lead_list.html',context)


def lead_detail(request,pk):
    leads = Lead.objects.get(id = pk)
    context = {
        'leads' : leads,
    }
    return render(request,'leads/lead_detail.html',context)


def lead_create(request):
    form = LeadModelForm()
    if request.method  == 'POST':
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/leads')
    context = {
        'form' : LeadForm()
    }
    return render(request,'leads/lead_create.html',context)


def lead_update(request,pk):
    lead = Lead.objects.get(id=pk)  
    form = LeadModelForm(instance=lead)
    if request.method  == 'POST':
        form = LeadModelForm(request.POST,instance=lead)
        if form.is_valid():
            form.save()
            return redirect('/leads')  
    context = {
        'form' : form,
         'leads' : leads,
    }
    return render ( request,'leads/lead_update.html')


def lead_delete(request,pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect('/leads/')   

"""
def lead_update(request,pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm()
    if request.method is == 'POST':
        print('RECEIVING A POST REQUEST')
        form = LeadModelForm(request.POST)
        if form.is_valid():
            print('The form is valid')
            print(form.cleaned_data)
            first_name = form.cleaned_data('first_name')
            last_name = form.cleaned_data('last_name')
            age = form.cleaned_data('age')
            agent = Agent.objects.first()
            lead.first_name = first_name
            lead.last_name = last_name
            lead.age = age
            lead.save()
            return redirect('/leads')
    context = {
        'form' : form,
         'leads' : leads,
    }
    return render ( request,'leads/lead_update.html') """
    



"""
 def lead_create(request):
    form = LeadModelForm()
    if request.method is == 'POST':
        print('RECEIVING A POST REQUEST')
        form = LeadModelForm(request.POST)
        if form.is_valid():
            print('The form is valid')
            print(form.cleaned_data)
            first_name = form.cleaned_data('first_name')
            last_name = form.cleaned_data('last_name')
            age = form.cleaned_data('age')
            agent = Agent.objects.first()
            Lead.objects.create(
                first_name= first_name,
                last_name= last_name,
                age = age,
                agent = agent,
            )
            return redirect('/leads')           


    context = {
        'form' : LeadForm()
    }
    return render(request,'leads/lead_create.html',context)

"""