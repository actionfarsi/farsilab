""" FITTING MODULE

TODO  add simple test-unit
"""

from numpy import *
from scipy.optimize import *



session_file = "session.txt"
last_results = None

class FittingFunction:
    def __init__(self):
        self.function = lambda x: 1
    def __call__(self,x):
        return self.function(x)

# From  www.scipy.org/Cookbook/FittingData :
# Modified to add uncertainties, full output
# =======================================
class Parameter:
    parameters = []
    def __init__(self, initialvalue, name, bounds = None):
        self.value = initialvalue
        self.name = name
        self.saved = initialvalue
        self.bounds = bounds
        Parameter.parameters.append(self)
    
    def set(self, value):
        self.value = value
        if self.bounds:
            self.value = max(self.bounds[0], value)
            self.value = min(self.bounds[1], value)
            
    def save(self):
        self.saved = self.value
    def load(self):
        self.value = self.saved

    def __call__(self):
        return self.value
    def __repr__(self):
        return "%s = %.3f" % (self.name,self.value)

def save_session():
    """Save all parameters (TODO and function)
    on file
    """
    import pickle
    pickle.dump(Parameter.parameters,open(session_file,'w'))

def load_session():
    """Save all parameters (TODO and function)
    on file
    """
    import pickle
    Parameter.parameters = pickle.load(open(session_file))
 
def fit(function, parameters, x, data, u, output = True, fit_method = None):
    """
    TODO add fitmethod hook
    TODO standardize residual with statistics.chisq
    """
    global last_results
    def residuals(params):
        for i,p in enumerate(parameters):
            p.set(params[i])   
        return ((data - function(x)) / u)
        
    
    p = [param() for param in parameters]
    ## TODO fit-method
    last_results = (leastsq(residuals, p, full_output=1,factor=10),
                    parameters,
                    len(x),)
    if last_results[1][-1] == False:
        print "Not converged"
        return
    
    if output:
        print post_fit()
    return last_results

def fit_simplex(function, parameters, x, data, u, outout=True):
    def fitfun(params):
        for i,p in enumerate(parameters):
            p.set(params[i])
        s = 0
        for i in range(len(data)):
            s += (((data[i] - function(x)[i])/u[i])**2).sum()
        return sqrt(s)
    
    p = [param() for param in parameters]
    return fmin(fitfun, p)


def post_fit():
    if last_results == None:
        return "No data"
    (p2,cov,info,mesg,success),parameters,ndata = last_results
    #print (p2,cov,info,mesg,success),parameters,ndata

    if not hasattr(p2,'__iter__'):
	p2 = [p2]

    out = ""

    out += "Initial values\n"
    for p in Parameter.parameters:
        out += "%10s = %10f\n"%(p.name, p.value)
    out += "\n"

    out += "Fitted values\n"
    for p in parameters:
        out += "%10s = %10f\n"%(p.name, p.value)
    out += "\n"
    
    ### calculate final chi square
    chisq=sum(info["fvec"]*info["fvec"])

    dof= ndata-len(parameters)
    ### chisq, sqrt(chisq/dof) agrees with gnuplot
    out += "Converged with chi squared %f\n" %chisq
    out += "degrees of freedom, dof %d\n" %dof
    out += "RMS of residuals (i.e. sqrt(chisq/dof)) %f\n" %sqrt(chisq/dof)
    out += "Reduced chisq (i.e. variance of residuals) %f\n" %(chisq/dof)
    out += "\n"

    if cov == None:
        out += "!!!! Null covariance matrix\n"
        return out

    ### uncertainties are calculated as per gnuplot, "fixing" the result
    ### for non unit values of the reduced chisq.
    ### values at min match gnuplot
    out += "Fitted parameters at minimum, with 68% C.I.:\n"
    for i,pmin in enumerate(p2):
        out += "%2i %-10s %12f +/- %10f\n"%(i,parameters[i].name,pmin,sqrt(cov[i,i])*sqrt(chisq/dof))
    out += "\n"

    out += "Correlation matrix\n"
    ### correlation matrix close to gnuplot
    out += "               "
    for p in parameters:
        out += "%-10s"%(p.name,)
    out += "\n"
    for i in range(len(p2)):
        out += "%10s"%(parameters[i].name)
        for j in range(i+1):
            out += "%10f"%(cov[i,j]/sqrt(cov[i,i]*cov[j,j]),)
        out += "\n"
    return out

import time

def save_post_plot():
    ### TODO add some contextual info in namefile    
    out = open("results.txt","a")
    out.write("\n--- FIT --- %s\n\n"%time.strftime("%d/%m/%y  %H:%M"))
    out.write(post_fit())
    out.close()

## Helper
def save_funz(funz,x,filename = "fitted.csv"):
    out = open(filename,'w')
    res = funz(x)
    for i in range(len(res)):
        out.write("%10e, %10e\n"%(x[i], res[i]))
        
