import numpy as np 
#import matplotlib.pyplot as plt 
#plt.rcParams['font.sans-serif']=['SimHei']
#plt.rcParams['axes.unicode_minus']=False
from astropy.io import fits 

def pack_spec(lumda,strength,n):
	lenth=len(lumda)
	k=int(lenth/n)

def check_num(lumda,n):
	if lumda[0]>lumda[-1]:
		b=len(lumda);a=0
		while b-a>1:
			c=int((a+b)/2)
			if lumda[c]>=n:
				a=c
			else:
				b=c
	else:
		b=len(lumda);a=0
		while b-a>1:
			c=int((a+b)/2)
			if lumda[c]>=n:
				b=c
			else:
				a=c
	if abs(lumda[a]-n)>abs(lumda[b]-n):
		return b
	else:
		return a

def gen_gaose_core(n,sigma):
	core=np.zeros(n)
	center=int((n+1.1)/2)
	for i in range(n):
		core[i]=np.exp(-(i+1-center)**2/2/sigma**2)/(2*np.pi)**0.5*sigma
	core=core/np.sum(core)
	return core

def core_convolution(core,datas):
	lenth_data=len(datas);lenth_core=len(core)
	k=int((lenth_core-0.9)/2)
	new_datas=np.r_[np.ones(k)*datas[0],datas,np.ones(k)*datas[-1]]
	return_data=np.zeros(lenth_data)
	for i in range(lenth_core):
		return_data+=new_datas[i:i+lenth_data]*core[i]
	return return_data

def plot_lines(lines,a,b):
	for i in range(len(lines)):
		plt.plot([lines[i],lines[i]],[a,b],'k--',linewidth=0.3)

#------------------------数据预处理及储存----------------------#
data=fits.open('J_A+A_587_A65_spvis.dat.gz.fits')[1].data
#Filename: J_A+A_587_A65_spvis.dat.gz.fits
#No.    Name      Ver    Type      Cards   Dimensions   Format
#  0  PRIMARY       1 PrimaryHDU      84   ()      
#  1  spvis.dat     1 TableHDU        24   4057462R x 3C   [F14.8, F17.15, F12.10]  
lenth=4057462
lumdas=np.zeros(lenth)
strength_normal=np.zeros(lenth)
strength_real=np.zeros(lenth)
for i in range(lenth):
	if i%10000==0:
		print(i)
	lumdas[i]=data[i][0]
	strength_normal[i]=data[i][1]
	strength_real[i]=data[i][2]
#plt.subplot(2,1,1)
#plt.plot(lumdas,strength_real,linewidth=0.1)
#plt.xlabel('$wave number(cm^{-1})$')
#plt.ylabel('$intensity$')
#plt.subplot(2,1,2)
#plt.plot(lumdas,strength_normal,linewidth=0.1)
#plt.xlabel('$wave number(cm^{-1})$')
#plt.ylabel('$relative-intensity$')
#plt.show()
np.save('lumda',lumdas)
np.save('strength_real',strength_real)
np.save('strength_normal',strength_normal)
#plt.plot(lumdas,strength_real)
#------------------------数据预处理及储存结束----------------------#

#--------------------------数据读取及处理-------------------------#
lumdas=np.load('lumda.npy')
strength_real=np.load('strength_real.npy')
strength_normal=np.load('strength_normal.npy')
#plt.plot(lumdas,strength_real,linewidth=0.1)
#plt.xlabel('$wave length($'+'$\lambda$'+'$)$')
#plt.ylabel('$intensity$')
#plt.show()

#修正比较大的一个误差（下三行）
kkk1=check_num(lumdas,6166.7)
kkk2=check_num(lumdas,6168.1)
strength_real[kkk2:kkk1]=(strength_real[kkk2-1]+strength_real[kkk1+1])/2
lines=[4101.1734,4340.472,4861.35,6562.79,5889.95095,5895.92424,4404.7501,5371.4893]
n=549;sigma=55
convolution_strength=core_convolution(gen_gaose_core(n,sigma),strength_real)
aaa=np.array([6401.9285,5755.8645,4765.953,4264.4107])
bbb=np.array([6562.79,5895.92424,4861.35,4340.472])
kkka=np.polyfit(aaa,bbb,4)
kkkb=np.poly1d(kkka)
lumda_moving=kkkb(lumdas)#lumda_moving为x，convolution_strength为y
#平均LAMOST:R_pix=4342.4453，波长范围为：3699.9863~9099.135
#平均:R_pix=4000000,	取921倍

#-------------------------生成积分谱---------------------#
sum_energy_spec=np.zeros(len(convolution_strength))
for i in range(len(convolution_strength)):
	sum_energy_spec[i]=np.sum(convolution_strength[:i+1])
	if i%10000==0:
		print(i)
np.save('sum_spec.npy',sum_energy_spec)
#------------------------生成积分谱结束--------------------#

LAMOST_lumdas=np.load('LAMOST_lumdas.npy')
sum_energy_spec=np.load('sum_spec.npy')
#plt.plot(lumda_moving,np.max(sum_energy_spec)-sum_energy_spec)
#plt.xlabel('$wave number(\lambda )$')
#plt.ylabel('$sum intensity$')
#plt.show()
calculus_sep=np.zeros(len(LAMOST_lumdas)+1)
calculus_sep[0]=LAMOST_lumdas[0]-abs(LAMOST_lumdas[1]-LAMOST_lumdas[0])/2
calculus_sep[-1]=LAMOST_lumdas[-1]+abs(LAMOST_lumdas[-2]-LAMOST_lumdas[-1])/2
for i in range(len(LAMOST_lumdas)-1):
	calculus_sep[i+1]=(LAMOST_lumdas[i]+LAMOST_lumdas[i+1])/2
#plt.scatter(np.linspace(1,len(LAMOST_lumdas)+1,len(LAMOST_lumdas)+1)-0.5,calculus_sep,s=1)
#plt.scatter(np.linspace(1,len(LAMOST_lumdas),len(LAMOST_lumdas)),LAMOST_lumdas,s=1)
#plt.show()
#!!!选取波长大于4200A的数据
calculus_sep=calculus_sep[check_num(calculus_sep,4200):]
LAMOST_lumdas=LAMOST_lumdas[check_num(LAMOST_lumdas,4200)+1:]
solar_Lamost_spec=np.zeros(len(LAMOST_lumdas))
#print(calculus_sep[0],calculus_sep[-1],lumda_moving[0],lumda_moving[-1])
for i in range(len(LAMOST_lumdas)):
	start_count=check_num(lumda_moving,calculus_sep[i]);stop_count=check_num(lumda_moving,calculus_sep[i+1])
	solar_Lamost_spec[i]=abs(sum_energy_spec[start_count]-sum_energy_spec[stop_count-1])
start=check_num(LAMOST_lumdas,6486.34);end=check_num(LAMOST_lumdas,6495.3135)
solar_Lamost_spec[start-1:end+2]=(solar_Lamost_spec[start-2]+solar_Lamost_spec[end+3])/2
solar_Lamost_spec=solar_Lamost_spec*10*10**12
lumda_spec=np.c_[LAMOST_lumdas,solar_Lamost_spec].T
np.save('lumda_spec.npy',lumda_spec)
lumda_spec=np.load('lumda_spec.npy')
#画图
#plt.plot(lumda_spec[0],lumda_spec[1],linewidth=0.3)
#plt.xlabel('$wave number(\lambda)$')
#plt.ylabel('$intensity$')
#plt.plot(lumdasc,convolution_strength,linewidth=0.1)
#plt.plot(lumdas,convolution_strength,linewidth=0.1)
#plt.show()
