import numpy as np
from numpy import exp #Wil be used during user function input
from numpy import log #Wil be used during user function input
from numpy import cos #Wil be used during user function input
from numpy import sin #Wil be used during user function input
from numpy import tan #Wil be used during user function input
from numpy import cosh #Wil be used during user function input
from numpy import sqrt #Wil be used during user function input
from numpy import pi #Wil be used during user function input

def elliot_ex(x,p):
    Eg=p[0]; #Bandgap
    Eb=p[1]; #Binding energy of exciton
    G=p[2]; #Broadening
    a=p[3]; #interband transition dipole moment
    n_ex=3; #take first 3 excitonic peaks
    y1=np.zeros(len(x))
    for i in range(n_ex):
        Ebi=Eg-Eb/((i+1)**2)
        y1=y1+(1/cosh((x-Ebi)/G)*(2*Eb))/((i+1)**3)
    y1=y1*(a**2)/x*sqrt(Eb)
    return y1

def elliot_cont(x,p):
    Eg=p[0]; #Bandgap
    Eb=p[1]; #Binding energy of exciton
    G=p[2]; #Broadening
    a=p[3]; #interband transition dipole moment
    b=p[4]; #eV^-1 , non-paraboliciy of bands
    E=np.linspace(Eg,Eg+(30*0.025),1000);
    y2=np.zeros(len(x))
    for i in range (len(x)):
        y2[i]=np.trapz( (1/cosh((x[i]-E)/G))/(1-exp(-2*pi*sqrt(Eb/(E-Eg))))*(1+b*(E-Eg)),E);
    y2=y2*(a**2)*sqrt(Eb)
    y2=y2/x
    return y2

