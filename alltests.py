#This script is for test purposes only, does not serve any other purpose in this project

ttorem = 'TAS'
test = ['TAS,PL-Mightex-csv,Abs-181,xycol,PL-PLE,abs_ade,3dmaker,xyrow,Ares_So,TRPL-ours,PPMS,PPMS_kumah,TAS_single_spec,THz,new_preset', 'row,1,2,1,col,2,1,1,comma,csv,xyz,2,2,not-flipped,Delay(ps),Wavelength(nm),${\\Delta}T/T$,x-Exist,y-Exist', 'col,1,2,1,col,1,3,1,comma,csv,xy,0,0,flipped,Wavelength(nm),Intensity(a.u.),Intensity(a.u.),x-Exist,y-Exist', 'col,3,1,1,col,3,2,1,comma,csv,xy,0,0,flipped,Wavelength(nm),Absorption(O.D.),Intensity(a.u.),x-Exist,y-Exist', 'col,1,1,1,col,1,2,1,comma,csv,xy,0,0,not-flipped,Wavelength(nm),Intensity(a.u.),Intensity(a.u.),x-Exist,y-Exist', 'col,2,1,1,col,2,2,1,comma,txt,xy,0,0,not-flipped,Wavelength(nm),Intensity(a.u.),Intensity(a.u.),x-Exist,y-Exist', 'col,1,1,1,col,1,2,1,comma,csv,xy,2,2,flipped,Wavelength_(nm),Absorption_(O.D.),Intensity(a.u.),x-Exist,y-Exist', 'row,1,2,1,col,2,1,1,comma,csv,xyz,2,2,not-flipped,Delay(x$10^1$$^2$_photons/s),Wavelength(nm),Intensity_(a.u.),x-Exist,y-Exist', 'row,1,1,1,row,2,1,1,comma,csv,xy,0,0,not-flipped,Wavelength(nm),Intensity(a.u.),Intensity(a.u.),x-Exist,y-Exist', 'none,1,2,1,row,1,1,1,space,txt,xyz,2,1,not-flipped,Angle_(deg),Wavelength(nm),Intensity_(a.u.),z-row,y-Exist', 'none,1,2,0.004,col,4,1,1,space,dat,xy,2,2,not-flipped,Delay(ns),Intensity_(a.u.),${\\Delta}T/T$,y-row/col,y-Exist', 'col,1,3,1,col,1,10,1,comma,dat,xy,2,2,not-flipped,Temperature(K),Resistivity(ohm/cm),Intensity_(a.u.),x-Exist,y-Exist', 'col,1,1,1,col,1,2,1,space,txt,xy,2,2,flipped,Temperature(K),Resistance(ohm),${\\Delta}T/T$,x-Exist,y-Exist', 'col,1,1,1,col,1,2,1,comma,csv,xy,0,0,not-flipped,Wavlength(ps),${\\Delta}T/T$,None,x-Exist,y-Exist', 'row,1,1,1,row,2,1,1,comma,csv,xy,2,2,not-flipped,Delay(ps),Intensity(a.u.),None,x-Exist,y-Exist', 'row,1,1,1,row,2,1,1,comma,csv,xy,0,0,not-flipped,Wavelength(nm),Intensity(a.u.),Intensity(a.u.),x-Exist,y-Exist']
ttitles = test[0].split(',')
indtorem = ttitles.index(ttorem)
del ttitles[indtorem]
ttitles=','.join(ttitles)
del test[indtorem+1]
test[0] = ttitles

impw_list = test