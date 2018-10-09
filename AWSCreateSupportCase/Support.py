class Support(object):
    def __init__(self):
        self._caseType = None

    @property
    def caseType(self):
        print("getter of caseType called")
        return self._caseType

    @caseType.setter
    def caseType(self, value):
        print("setter of caseType called")
        self._caseType = value

    @caseType.deleter
    def caseType(self):
        print("deleter of caseType called")
        del self._caseType
        
    @property
    def serviceType(self):
        print("getter of serviceType called")
        return self._serviceType

    @serviceType.setter
    def serviceType(self, value):
        print("setter of serviceType called")
        self._serviceType = value

    @serviceType.deleter
    def serviceType(self):
        print("deleter of serviceType called")
        del self._serviceType
        
    @property
    def category(self):
        print("getter of category called")
        return self._category

    @category.setter
    def category(self, value):
        print("setter of category called")
        self._category = value

    @category.deleter
    def category(self):
        print("deleter of category called")
        del self._category
        
    @property
    def severityType(self):
        print("getter of severityType called")
        return self._severityType

    @severityType.setter
    def severityType(self, value):
        print("setter of severityType called")
        self._severityType = value

    @severityType.deleter
    def severityType(self):
        print("deleter of severityType called")
        del self._severityType
      
    @property  
    def subject(self):
        print("getter of subject called")
        return self._subject

    @subject.setter
    def subject(self, value):
        print("setter of subject called")
        self._subject = value

    @subject.deleter
    def subject(self):
        print("deleter of subject called")
        del self._subject
        
    @property  
    def description(self):
        print("getter of description called")
        return self._description

    @description.setter
    def description(self, value):
        print("setter of description called")
        self._description = value

    @description.deleter
    def description(self):
        print("deleter of description called")
        del self._description
        
    @property  
    def categoryList(self):
        print("getter of categoryList called")
        return self._categoryList

    @categoryList.setter
    def categoryList(self, value):
        print("setter of categoryList called")
        self._categoryList = value

    @categoryList.deleter
    def categoryList(self):
        print("deleter of categoryList called")
        del self._categoryList