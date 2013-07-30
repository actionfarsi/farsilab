
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//#include <cuda.h>
//#include <cuda_runtime.h>
#include "CUDAFFT test.h"

__global__ void zwap(double *u_mat,int x_s, int y_s)
    {
		const int y = blockDim.y * blockIdx.y + threadIdx.y;
		const int x = blockDim.x * blockIdx.x + threadIdx.x;
		u_mat[(x*y_s+y)*2]=u_mat[(x*y_s+y)*2];
	}
	
__global__ void phaseMulti(double *u_mat,int x_s, int y_s, double *kx, double *ky, double dz)
{
		const int y = blockDim.y * blockIdx.y + threadIdx.y;
		const int x = blockDim.x * blockIdx.x + threadIdx.x;
		double dur=0,dui=0,ur,ui;

		dur=cos((kx[x]+ky[y])*dz);
		dui=sin(-(kx[x]+ky[y])*dz);
		
		ur=u_mat[(x*y_s+y)*2];
		ui=u_mat[(x*y_s+y)*2+1];
		
		u_mat[(x*y_s+y)*2]=ur*dur-ui*dui;
		u_mat[(x*y_s+y)*2+1]=ur*dui+ui*dur;
}

__global__ void normalizeAfterFFT(double *u_mat,int x_s, int y_s, double x_smy_sI)
{
		const int y = blockDim.y * blockIdx.y + threadIdx.y;
		const int x = blockDim.x * blockIdx.x + threadIdx.x;
		u_mat[(x*y_s+y)*2]=u_mat[(x*y_s+y)*2]*x_smy_sI;
		u_mat[(x*y_s+y)*2+1]=u_mat[(x*y_s+y)*2+1]*x_smy_sI;
	
}		

__global__ void nonlinear(double *u_mat,int x_s, int y_s, double beta, double dz, double *keepMax, int step)
{
		const int y = blockDim.y * blockIdx.y + threadIdx.y;
		const int x = blockDim.x * blockIdx.x + threadIdx.x;
		double I;
		I=u_mat[(x*y_s+y)*2]*u_mat[(x*y_s+y)*2]+u_mat[(x*y_s+y)*2+1]*u_mat[(x*y_s+y)*2+1];

		double dur=0,dui=0,ur,ui;

		dur=cos(I*beta*dz);
		dui=sin(I*beta*dz);
		
		ur=u_mat[(x*y_s+y)*2];
		ui=u_mat[(x*y_s+y)*2+1];
		
		u_mat[(x*y_s+y)*2]  =ur*dur-ui*dui;
		u_mat[(x*y_s+y)*2+1]=ur*dui+ui*dur;
	
		if ((x==x_s/2) && (y==y_s/2))
			keepMax[step]=I;
	
}		

extern "C" void runNonlinear(double *u_mat,int x_s, int y_s, double beta, double dz, double *keepMax, int step)
{
		dim3 numBlocks(32,32);
		dim3 threadsPerBlock(32,32);
		nonlinear<<<numBlocks,threadsPerBlock>>>(u_mat, x_s, y_s, beta, dz, keepMax, step);
}		


extern "C" void runNormalizeAfterFFT(double *u_mat,int x_s, int y_s)
{
		dim3 numBlocks(32,32);
		dim3 threadsPerBlock(32,32);
		double pdblfactor = 1./(x_s*y_s);
		normalizeAfterFFT<<<numBlocks,threadsPerBlock>>>(u_mat, x_s, y_s, pdblfactor);
}		


extern "C" void runPhaseMulti(double *u_mat,int x_s, int y_s, double *kx, double *ky, double dz)
{
		dim3 numBlocks(32,32);
		dim3 threadsPerBlock(32,32);
		phaseMulti<<<numBlocks,threadsPerBlock>>>(u_mat,x_s, y_s, kx, ky, dz);
}	
	
extern "C" void runZwap(double *u_mat, int x_s, int y_s)
	{
		
		dim3 numBlocks(32,32);
		dim3 threadsPerBlock(32,32);
		zwap<<<numBlocks,threadsPerBlock>>>(u_mat,x_s,y_s);	
	}
