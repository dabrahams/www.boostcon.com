from django import newforms as forms

if not hasattr(forms.Form, 'cleaned_data'):
   def get_cleaned_data(self):
       return self.clean_data
   def set_cleaned_data(self, v):
       self.__dict__['cleaned_data'] = v
   forms.Form.cleaned_data = property(get_cleaned_data, set_cleaned_data)
   
