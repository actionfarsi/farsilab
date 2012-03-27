# Major library imports
import random
import wx
from numpy import arange, array, hstack, random

# Enthought imports
from enthought.traits.api import Array, Bool, Callable, Enum, Float, HasTraits, \
                                 Instance, Int, Trait
from enthought.traits.ui.api import Group, HGroup, Item, View, spring, Handler
from enthought.pyface.timer.api import Timer

# Chaco imports
from enthought.chaco.chaco_plot_editor import ChacoPlotItem

from freqcounter import FreqTask

class Viewer(HasTraits):
    """ This class just contains the two data arrays that will be updated
    by the Controller.  The visualization/editor for this class is a 
    Chaco plot.
    """
    
    index = Array
    
    data = Array

    plot_type = Enum("line", "scatter")
    
    # This "view" attribute defines how an instance of this class will
    # be displayed when .edit_traits() is called on it.  (See MyApp.OnInit()
    # below.)
    view = View(ChacoPlotItem("index", "data",
                               type_trait="plot_type",
                               resizable=True,
                               x_label="Time",
                               y_label="Signal",
                               y_bounds = (0,100000),
                               y_auto = False,
                               color="blue",
                               bgcolor="white",
                               border_visible=True,
                               border_width=1,
                               padding_bg_color="lightgray",
                               width=800,
                               height=380,
                               show_label=False),
                HGroup(spring, Item("plot_type", style='custom'), spring),
                resizable = True,
                buttons = ["OK"],
                width=800, height=500)

class MyApp(wx.PySimpleApp):
    
    def OnInit(self, *args, **kw):
        viewer = Viewer()
        #controller = Controller(viewer = viewer)
        
        # Pop up the windows for the two objects
        viewer.edit_traits()
        #controller.edit_traits()
        
        # Set up the timer and start it up
        self.setup_ts(viewer)
        return True


    def setup_ts(self, viewer):
        ts = FreqTask(1,0.7)
        def update(x):
            print x
            cur_data = viewer.data
            new_data = hstack((cur_data[-100+1:], [x]))
            new_index = arange(100)
        
            viewer.index = new_index
            viewer.data = new_data
        
        ts.thread_read(update)
        return


# This is called when this example is to be run in a standalone mode.
if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()    

# EOF
