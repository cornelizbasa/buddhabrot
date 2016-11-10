from __future__ import division
from bokeh.io import output_notebook, show
from bokeh.plotting import figure
import numpy as np

class Image:
    "2D matrix as list of lists"
    def __init__(self,x,y):
        self.reset(x,y)
    
    def __getitem__(self,i):
        return self.img[i]

    def clear(self):
        for i in range1d(self.x):
            for j in range1d(self.y):
                self.img[j][i]=0

    def reset(self,x,y):
        self.x=x; self.y=y
        self.img=[[0 for i in range(self.x)] for j in range(self.y)]
        self.clear()

class ComplexFractal(Image):
    "Abstract complex fractal"
    maxit = 128
    def __init__(self,minz,maxz,**kwargs):
        self.__dict__.update(kwargs)
        self.at(minz, maxz)
        Image.__init__(self,self.x,self.y)

    def at(self,minz,maxz): 
        self.minz = minz; self.maxz = maxz
        self.d = self.maxz-self.minz
        self.x = int(self.scale * self.d.real); self.y = int(self.scale * self.d.imag)

    def coords(self,z):
        return self.coordx(z), self.coordy(z)

    def coordx(self,z):
        return int((z.real-self.minz.real) / self.d.real * self.x)

    def coordy(self,z):
        return int(self.y-(z.imag-self.minz.imag) / self.d.imag * self.y)

    def z(self,i,j):
        return complex(self.minz.real + i * self.d.real / self.x,
                       self.minz.imag + (self.y-j) * self.d.imag / self.y)

    def render(self):
        self.im = np.empty((self.x, self.y), dtype=np.uint32)
        self.view = self.im.view(dtype=np.uint8).reshape((self.x, self.y, 4))
        for i in range(self.x):
            for j in range(self.y):
                self.view[j][i][0]=self.fractal(self.z(i,j))

    def draw(self):
        self.render()
        p = figure(plot_width=self.x, plot_height=self.y)
        p.image_rgba(image=[self.img],x=[0],y=[0],dw=[self.x],dh=[self.y])
        show(p)
                        
class Mandelbrot(ComplexFractal):
    "Mandelbrot fractal"
    julia = None

    def __init__(self,minz,maxz,**kwargs):
        ComplexFractal.__init__(self,minz,maxz,**kwargs)

    def fractal(self,c):
        i = 0; z = self.julia and c or 0
        while i<self.maxit:
            z=z*z+(self.julia or c)
            if abs(z)>=2: 
                return self.maxit-i
            i+=1
        return 0

class Buddhabrot(Mandelbrot):
    "Buddhabrot rendering of the Mandelbrot set"

    def __init__(self,minz,maxz,**kwargs):
        Mandelbrot.__init__(self,minz,maxz,**kwargs)

    def plot(self,l):
        for e in l:
            x, y = self.coords(e)
            if x >= 0 and x < self.x and y >= 0 and y < self.y:
                self.img[y][x]+=1
                c = self.img[y][x]
                if c > self.max:
                    self.max = c

    def onebuddha(self,c):
        i = 0; z = self.julia and c or 0
        l = []
        while i<self.maxit:
            z=z*z+(self.julia or c)
            l.append(z)
            if abs(z)>=2:
                return self.plot(l)
            i+=1
        return 0

    def render(self):
        self.max = 0
        g = rangecomplex(self.minz,self.maxz,self.stepz)
        i = 0; total = int((1+self.d.real / self.stepz.real) * (1+self.d.imag / self.stepz.imag))
        ftotal=100/float(total); total/=100
        for z in g:
            i+=1
            if i % total == 0:
                print '%3d%%' % int(i*ftotal)
            self.onebuddha(z)

        for i in range1d(self.x):
            for j in range1d(self.y):
                self.img[j][i]=int(self.img[j][i]/float(self.max)*255)

def range1d(a,b=None,step=1,f=None):
    if not b:
        b = a
        a = 0        
    i = a
    while i < b:
        yield f and f(i) or i
        i+=step

def range2d(x1,x2,y1,y2,stepx=1,stepy=1,f=None):
    i = x1
    while i < x2:
        j = y1
        while j < y2:
            yield f and f(i,j) or (i, j)
            j+=stepy
        i+=stepx

def rangecomplex(minz,maxz,stepz,f=None):
    return range2d(minz.real,maxz.real,minz.imag,maxz.imag,stepz.real,stepz.imag,
                   f and (lambda x,y: f(complex(x,y))) or complex)

mandel = Mandelbrot(-2-1.5j,1+1.5j,title='Mandelbrot',scale=200).draw()
#buddha = Buddhabrot(-2-1.5j,1+1.5j,stepz=0.0005+0.0005j,title='Buddhabrot',maxit=64,scale=300).draw()


