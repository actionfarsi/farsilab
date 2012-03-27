"""Testing the cuFFT process with the Nvidia Tesla

#   Programmed and copyright by Sam Schrauth
#   Advisor: Alex Gaeta
#   Quantum and Nonlinear Photonics Group
#   School of Applied and Engineering Physics
#   Cornell Univeristy    2011"""

from numpy import *
import time

import pycuda.autoinit
import pycuda.gpuarray as gpuarray
from pycuda.compiler import SourceModule
from pycuda.tools import make_default_context,dtype_to_ctype
from pycuda.elementwise import get_axpbyz_kernel,get_axpbz_kernel, get_binary_op_kernel, ElementwiseKernel
from pycuda.driver import Stream, Context

from pycuda import cumath
from pyfft.cuda import Plan
from numpy.fft import fftfreq
from matplotlib import pylab as pl

#print dtype_to_ctype(complex64)

N_Z = 400000 ##maximum z step
NMAX = 8192
NMAXSQRT = 64
pi = 3.141592

## Default input parameter specification
r=0.5
nz=5

def main():
    ## Default input parameter specification
    r=1.0
    nz=100
    G=1.8962

    print("Starting\n")
    start_time = time.time()

    print("Creating Initial Profile\n")
    ##simulation parameter
    n_points = (1024,1024)
    Xmax= (5.0,5.0) #  grid and window
    dx = [2.*Xmax[i]/n_points[i] for i in [0,1]]

    dz=0.003
    beta = 500

    #print "Enter step size [Ldf]\n" 
	#scanf("%lf",&dz 
    #print "Enter number of steps \n" 
	#scanf("%lf",&nz 
	#nz=(int)nz;
	#print "Enter number of critical powers\n" 
	#scanf("%lf",&beta 
    gamma=G*beta

    x=linspace(-Xmax[0],Xmax[0],n_points[0])
    y=linspace(-Xmax[1],Xmax[1],n_points[1])
    
    kx=fftfreq(n_points[0],dx[0])
    ky=fftfreq(n_points[1],dx[1])
    
    X,Y = meshgrid(x,y)
    Kx, Ky = meshgrid(kx,ky)
    
    keepMax=zeros(N_Z)

    II_out= zeros(n_points)
    U_m = zeros(n_points, dtype = complex64)
    IM_out= zeros(n_points)
    IF_out= zeros(n_points)
    ufft= zeros(n_points, dtype = complex64)
    ufft_pc= zeros(n_points, dtype = complex64)

	##for (j=0;j<nx;j++) {
	##	x[j]=(double)(-nx/2+j+1)*dx;
	##	kx[j]=(j < nx/2 ) ?
    ##             (pi*(double)(j))*(1./dx/((double)(nx))):
    ##             (pi*(double)(j-nx))*(1./dx/((double)(nx))    ##fx_s=1/dx, dfx= fx_s/N-> d omega= 2pi dfx		
	## ?????	kx[j]=kx[j]*kx[j];
	
    u = exp( -(X**2 + Y**2)/r ) + 0.j
    u = u.astype(complex64)
    
    u_m= zeros(n_points)
    u_f= zeros(n_points)
    
    II_out = (u.real**2 + u.imag**2)  ## ???
	
    steps=2.*nz

    print "Step size %g [Ldf]\n"%dz
    print "Number of critical powers %g\n"%beta
    print "Number of steps %d\n"%N_Z


    ## cuFFT planning and preparation
    # cuda.init()
    dev = pycuda.autoinit.device
    context = make_default_context()
    
    nonlinearMod = SourceModule("""
 #include <pycuda-complex.hpp>

__global__ void nonlinear(pycuda::complex<float> *u_mat, float beta, float dz, pycuda::complex<float> *keepMax, int step)
{
		const int y = blockDim.y * blockIdx.y + threadIdx.y;
		const int x = blockDim.x * blockIdx.x + threadIdx.x;
		float I;
        pycuda::complex<float> I_UNIT(0.,1.);
        int i = x* %(n)d + y;
        
		I=pycuda::abs(u_mat[i]);

		u_mat[i]= u_mat[i]* pycuda::exp(I_UNIT*I*beta*dz);
		
		if ((x==i/2) && (y==i/2))
			keepMax[step]=pycuda::exp(I_UNIT*I*beta*dz);
	
}
    
__global__ void prod(pycuda::complex<float> *X,
                     pycuda::complex<float> *Y, pycuda::complex<float> *Z)
{
		const int y = blockDim.y * blockIdx.y + threadIdx.y;
		const int x = blockDim.x * blockIdx.x + threadIdx.x;
        int i = x*%(n)d + y;
		Z[i]=X[i] * Y[i];
	
    }"""%{'n' : n_points[0]})

    
    print "Device %d: \"%s\" with Compute %d.%d capability\n"%(dev.pci_bus_id,
                                                               dev.name(),
                                                               dev.compute_capability()[0],
                                                               dev.compute_capability()[1])
    print "Creating FFT Plans\n"
	
    
    plan = Plan(n_points, wait_for_finish = True, scale = dx[0]*dx[1])
    block = (16,16,1)
    grid = (n_points[0]/block[0],
            n_points[1]/block[1])   ## Threads per block
    fft_g  = lambda x, y: plan.execute(x, y)
    ifft_g = lambda x, y: plan.execute(x, y, inverse = True)
    
    g_mult = nonlinearMod.get_function('prod')
    runNonLinear = nonlinearMod.get_function("nonlinear")
    
    print "Allocating memory on device\n"
    u_gpu = gpuarray.to_gpu(u.astype(complex64))
    U_gpu = gpuarray.to_gpu(zeros(n_points, complex64))


    print "Allocating kx, ky & keepMax\n" 
    cukx = gpuarray.to_gpu(kx)
    cuky = gpuarray.to_gpu(ky)
    cukeepMax = gpuarray.to_gpu(ones(nz, complex64))
 
	## preparing the data to transfer to the device 
    
    IM_out = u.real
    #fileout("A",0.,h_in,nx, ny) 
    
    print "Starting %i FFT pairs\n"%steps
    start = time.time()

    op_diff = exp(5e2j*(Kx**2+Ky**2) *dz/2.)
    op_diff = gpuarray.to_gpu(op_diff.astype(complex64))
    
    zero_j = array([0],dtype = complex64)
    one_j = array([1],dtype = complex64)
    idxdy = array([1./(dx[0]*dx[1])], dtype = complex64)
    dxdy = array([(dx[0]*dx[1])], dtype = complex64)
    
    g_mult(U_gpu, op_diff, U_gpu, block = block, grid = grid)
    context.synchronize()
    #print abs(U_gpu.get())
    #pl.imshow(abs(U_gpu.get()))
    #pl.figure()
    
    for l in xrange(nz):
		## FFT into the spatial frequency domain
        fft_g(u_gpu, U_gpu)
        g_mult(U_gpu, op_diff, U_gpu, block = block, grid = grid)
        context.synchronize()
        
		## inverse FFT into space domain
        ifft_g(U_gpu, u_gpu)
        
    	
		## Nonlinear step in space domain
        runNonLinear(u_gpu, float32(gamma), float32(dz), cukeepMax, int32(l), block = block, grid = grid)
        context.synchronize()
		## cast to double
        fft_g(u_gpu, U_gpu)
        
        g_mult(U_gpu, op_diff, U_gpu, block = block, grid = grid)
        context.synchronize()
		## inverse FFT into space domain
        ifft_g(U_gpu, u_gpu)
        
    
http://rstudio.org/http://rstudio.org/
    print "Finished FFTs\n" 
    end = time.time()
    time_SEC = (end-start)
    print "The time was %g seconds\n"%time_SEC 
    print cukeepMax.get()
    pl.imshow(abs(u_gpu.get()))
    pl.show()
    
    #fileout("KeepMax",0.,keepMax,nz)
  
	# restor to u_f
    #fileout("E",0.,h_out,nx, ny)
    #to_comp2d(nx,ny,u_m,U_m)

    #IM_out = u_m.real**2 + u_m.imag**2
  
    ## memory clean-up
    print "Memory Cleanup\n"
    context.pop()
  # time_h = (end-start)/CLK_TCK/3600;
  # time_HR = floor(time_h 
  # time_MIN = floor((time_h-time_HR)*60.0+0.5 
  
    print "Done!\n"
    raw_input()
    return 0


def to_real2d(a, b = None):
	"Interleave"
	if b == None:
		b = zeros(a.shape[0],2*a.shape[1])
	for j in a.shape[0]:
		for k in a.shape[1]:
			b[j][2*k]= real(a[j][k])
			b[j][2*k+1]=imag(a[j][k]) 
	return b

def to_comp2d(a,b):
    for j in a.shape[0]:
        for k in a.shape[1]:
            a[j][k]=b[j][2*k]+1j*b[j][2*k+1]
            
if __name__ == "__main__":
    main()
            