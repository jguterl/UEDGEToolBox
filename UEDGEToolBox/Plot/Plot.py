#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 23:11:01 2020

@author: jguterl
"""
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod, SetClassArgs
from mpl_toolkits.axes_grid1 import make_axes_locatable
from UEDGEToolBox.Plot.PlotUtils import UBoxPlotUtils
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

from UEDGEToolBox.DataManager.DataParser import UBoxDataParser
from UEDGEToolBox.DataManager.Grid import UBoxGrid
from mpl_toolkits.axes_grid1 import ImageGrid
from UEDGEToolBox.Utils.Misc import ClassInstanceMethod, SetClassArgs, AddPrintMethod
from UEDGEToolBox.Plot.PlotUtils import MatplotlibKw


class UBoxPlot1D(UBoxPlotUtils):
    def __init__(self):
        pass

    @staticmethod
    def CheckShape1DData(x, data):
        if len(data.shape) > 1:
            return False
        if x is not None and len(x) != data.shape[0]:
            return False
        else:
            return True

    def PlotSeparatrix(self, rm, zm, iysptrx, ax=None, color='r', linewidth=1, **kwargs):

        pass
        # if ax is None:
        #     ax=plt.gca()

        # ax.plot((rm[:,iysptrx,3]),ax.get_ylim(),color=color,linewidth=linewidth,**kwargs)

    def PlotData1D(self, x, data, Label=None, ShowLegend=False, **kwargs):
        ax = self.GetAx(**kwargs)

        if type(x) == list:
            p = []
            for x_, data_ in zip(x, data):
                p.extend(ax.plot(x_, data_, **self.PlotKw(**kwargs)))
        else:
            p = ax.plot(x, data, **self.PlotKw(**kwargs))
        if Label is not None:
            if type(Label) != list:
                Label = [Label]
            for pp, l in zip(p, Label):
                pp.set_label(l)

        if type(p) != list:
            p = [p]
        return p



    def Check1DDim(XData, Data):
        if type(XData) == np.ndarray and len(XData.shape) > 1:
            return False
        if type(Data) == np.ndarray and len(Data.shape) > 1:
            return False
        return True

    def PickLabel(self, Grid):
        if len(Grid.shape) > 1:
            if Grid.shape[0] == 1:
                XLabel = 'Z [m]'
                YLabel = None
            elif Grid.shape[1] == 1:
                XLabel = 'R [m]'
                YLabel = None
            else:
                XLabel = 'R [m]'
                YLabel = 'Z [m]'

        return (XLabel, YLabel)


class UBoxPlot2D(UBoxPlotUtils):
    ax = None

    def __init__(self):
        pass

    @staticmethod
    def CheckShape2DData(r, z, data):
        return not (r.shape[0] != z.shape[0] or r.shape[1] != z.shape[1] or data.shape[0] != r.shape[0] or data.shape[1] != r.shape[1])

    @ClassInstanceMethod
    def PlotterSeparatrix2D(self, Grid=None, color='r', label='separatrix', linewidth=1, ax=None, **kwargs):
        Grid = self.GetGridPlot(Grid)

        if Grid is not None:
            r = Grid.get('rm')
            z = Grid.get('zm')
            iysptrx = Grid.get('iysptrx') - 1  # shift array for python

        if z is None or r is None or iysptrx is None:
            print('Something went wrong when processing the grid... Cannot plot separatrix')
            return

        self.PlotDataSeparatrix2D(r, z, iysptrx, color, label, linewidth, **kwargs)

    @ClassInstanceMethod
    def PlotDataSeparatrix2D(self, rm, zm, iysptrx, color='r', label='separatrix', linewidth=1, ax=None, **kwargs):
        sepx = np.concatenate((rm[:, iysptrx, 3], np.array([rm[-1, iysptrx, 4]])))
        sepy = np.concatenate((zm[:, iysptrx, 3], np.array([zm[-1, iysptrx, 4]])))

        ax = self.GetAx(ax)
        ax.plot(sepx, sepy, color=color, linewidth=linewidth, label=label, **kwargs)

    @ClassInstanceMethod
    def CreatePatchCollection(self, r, z, data, Label, DataLim, DataScale, ColorMap):
        if not self.CheckShape2DData(r, z, data):
            print('Mismatch between shapes of r,z and data:{},{} and {}'.format(r.shape, z.shape, data.shape))
            return (None, {}, {}, {})

        Nx = len(r)
        Ny = len(r[0])
        data = data.reshape(Nx * Ny)

        if DataLim is None:
            DataLim = (min(data), max(data))
        patches = []
        idx = [np.array([1, 2, 4, 3, 1])]
        Dic = {}
        Pos = {}
        Obj = {}
        for i in range(Nx):
            for j in range(Ny):
                Data = np.concatenate((r[i, j, idx], z[i, j, idx])).reshape(2, 5).T
                p = matplotlib.patches.Polygon(Data, closed=True, edgecolor=None, label='ix={},iy={}'.format(i, j), picker=5)
                patches.append(p)

                Obj[p] = p
                Dic[p] = 'ix={},iy={}'.format(i, j)
                Pos[p] = (r[i, j, 0], z[i, j, 0])

        Collec = matplotlib.collections.PatchCollection(patches)
        Collec.set_picker(True)
        if DataScale == 'log':
            norm = matplotlib.colors.LogNorm(vmin=DataLim[0], vmax=DataLim[1])
        elif DataScale == 'symlog':
            norm = matplotlib.colors.SymLogNorm(vmin=DataLim[0], vmax=DataLim[1])
        elif DataScale == 'linear':
            norm = matplotlib.colors.Normalize(vmin=DataLim[0], vmax=DataLim[1])
        else:
            print('Unknow DataScale. Must be log|symlog|linear')
            return (None, {}, {}, {})
        Collec.set_array(data)
        Collec.set_cmap(ColorMap)
        Collec.set_norm(norm)
        Collec.set_clim(vmin=DataLim[0], vmax=DataLim[1])
        if Label is not None:
            Collec.set_label(Label)
        return (Collec, Dic, Pos, Obj)

    @ClassInstanceMethod
    def PlotData2D(self, r, z, data, Label=None, ColorMap='jet', DataLim=None, DataScale='linear', ScaleFactor=1.0, ColorBar=True, **kwargs):
        """Plot UEDGE grid."""
        PlotHandle = []
        if ColorMap not in matplotlib.pyplot.colormaps():
            print('ColorMap {} not defined in matplotlib...')
            print('ColorMap must be chosen in the following list:')
            print(matplotlib.pyplot.colormaps())
            return
        # print(kwargs.get('ax'))
        ax = self.GetAx(**kwargs)
        # cax=self.GetCAx(**kwargs)
        # print(kwargs.get('ax'))
        data = ScaleFactor * data
        (Collec, Dic, Pos, Obj) = self.CreatePatchCollection(r, z, data, Label, DataLim, DataScale, ColorMap)

        if Collec is not None:

            def onpick(evt):
                if evt.artist == Collec:
                    print(evt.artist.get_array()[evt.ind[0]])
                if evt.artist in Pos.keys():
                    annot.set_visible(False)
                    annot.xy = Pos[evt.artist]
                    evt.artist.set_facecolor = 'blue'
                    evt.artist.set_fill = True
                    annot.set_text(Dic[evt.artist])
                    annot.set_visible(True)
                if evt.mouseevent.button == 3:
                    annot.set_visible(False)


            PlotHandle.append(ax.add_collection(Collec))

            ax.set_ylim(z.min(), z.max())
            ax.set_xlim(r.min(), r.max())
            annot = ax.annotate("", xy=(0, 0), xytext=(-20, 20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="->"))
            annot.set_visible(False)
            ax.set_aspect('equal')
            ax.figure.canvas.mpl_connect('pick_event', onpick)
            if ColorBar:
                self.AddColorBar(Collec, ax, **kwargs)

            return PlotHandle
        else:
            return None

    @ClassInstanceMethod
    def AddColorBar(self, Collec, ax, LocationColorBar='right', SizeColorBar='5%', PadColorBar=0.3, **kwargs):
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(LocationColorBar, SizeColorBar, PadColorBar)
        self.cax = ax.figure.colorbar(Collec, cax=cax)

    @ClassInstanceMethod
    def SetAx(self):
        ax.set_aspect('equal', 'box')


@AddPrintMethod(2)
class UBoxDataPlotter(UBoxPlot2D, UBoxPlot1D, UBoxPlotUtils):

    def __init__(self, DataStruct=None, **kwargs):
        self.DataStruct = []
        self.DataStructName = []
        self.ExtraLabels = []
        self.DataSpecies = []
        self.CaseName = []
        self.PlotDim = None
        self.AxisType = None
        self.XData = []
        self.YData = []
        self.XYData = []
        self.Labels = []
        self.Tag = []
        self.ax_settings = {}
        self.AutoUnits = True
        self.AutoLabels = True
        self.YLabel = None
        self.XLabel = None
        self.PlotLabel = None
        self.PlotTitle = None
        self.PlotHandle = []
        self.ax = None
        self.Verbose = False
        if kwargs.get('Verbose') is not None:
            self.Verbose = kwargs.get('Verbose')
        if DataStruct is not None:
            self.AddPlotData(DataStruct, **kwargs)

    def SetAxProperties(self, **kwargs):
        if self.ax is not None:
            List = MatplotlibKw.Axes()
            Dic = dict((k, v) for (k, v) in kwargs.items() if k in List)
            for (k, v) in Dic.items():
                if hasattr(self.ax, 'set_{}'.format(k)):
                    self.VerbosePrint('Applying set_{}({})'.format(k, v))
                    getattr(self.ax, 'set_' + k)(v)

    @staticmethod
    def GetStyleList(Attribute, Value):

        ListLineStyleDefault = [
            ('solid', 'solid'),      # Same as (0, ()) or '-'
            ('dotted', 'dotted'),    # Same as (0, (1, 1)) or '.'
            ('dashed', 'dashed'),    # Same as '--'
            ('dashdot', 'dashdot'),  # Same as '-.'
            ('loosely dotted', (0, (1, 10))),
            ('dotted', (0, (1, 1))),
            ('densely dotted', (0, (1, 1))),

            ('loosely dashed', (0, (5, 10))),
            ('dashed', (0, (5, 5))),
            ('densely dashed', (0, (5, 1))),

            ('loosely dashdotted', (0, (3, 10, 1, 10))),
            ('dashdotted', (0, (3, 5, 1, 5))),
            ('densely dashdotted', (0, (3, 1, 1, 1))),

            ('dashdotdotted', (0, (3, 5, 1, 5, 1, 5))),
            ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
            ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))]

        if Attribute == 'color':
            if Value == 'default':
                return plt.rcParams['axes.prop_cycle'].by_key()['color']
            else:
                if type(Value) != list:
                    Value = [Value]
                return Value

        if Attribute == 'linestyle':
            if Value == 'default':
                return [L[1] for L in ListLineStyleDefault]
            else:
                if type(Value) != list:
                    Value = [Value]
                return Value

    def SetLineProperties(self, **kwargs):
        ListAttributes = ['color', 'linestyle']
        for Attribute in ListAttributes:
            if type(kwargs.get(Attribute)) == dict:
                for DataProperty, Style in kwargs[Attribute].items():
                    ListStyle = self.GetStyleList(Attribute, Style)
                    if hasattr(self, DataProperty):
                        ListDataProperty = getattr(self, DataProperty)
                        DicAttribute = self.MakeDicStyle(ListDataProperty, ListStyle)
                        #print(Attribute, DicAttribute, ListDataProperty)
                        for p, DP in zip(self.PlotHandle, ListDataProperty):
                            if hasattr(p, 'set_{}'.format(Attribute)):
                                f = getattr(p, 'set_{}'.format(Attribute))
                                #print(Attribute, DicAttribute[DP])
                                f(DicAttribute[DP])

                    else:
                        self.Print('Cannot find property "{}" in DataPlotter)'.format(DataProperty))

    def SetLabel(self, SetupLabels=[], **kwargs):
        if type(SetupLabels) != list:
            SetupLabels = [SetupLabels]

        for P, DS, EL, T in zip(self.PlotHandle, self.DataSpecies, self.ExtraLabels, self.Tag):
            Label = []
            if 'Project' in SetupLabels:
                Label.append(T.get('Project'))
            if 'CaseName' in SetupLabels:
                Label.append(T.get('CaseName'))
            if 'DataSpecies' in SetupLabels:
                Label.append(DS)
            if 'ExtraLabels' in SetupLabels:
                Label.append(EL)
            if Label != []:
                P.set_label(' | '.join(Label))

    def SetLegend(self,**kwargs):
        Dic = self.LegendKw(**kwargs)
        self.PrintVerbose('Legend settings:',Dic)
        self.ax.legend(**Dic)

    @staticmethod
    def MakeDicStyle(DataProperty, ListStyle):
        DicStyle = {}
        Style = iter(ListStyle)
        for P in DataProperty:
            if DicStyle.get(P) is None:
                DicStyle[P] = next(Style)
        return DicStyle

    def AddPlotData(self, DataStruct, **kwargs):
        if kwargs.get('Verbose') is not None:
            self.Verbose = kwargs.get('Verbose')

        if type(DataStruct) != list:
            DataStruct = [DataStruct]
        # Check consistency of PlotType and axistype
        for D in DataStruct:
            PlotDim = D.get('PlotDim')
            AxisType = D.get('AxisType')
            self.DataName = D.get('DataName')
            self.DataStructName.append(D.get('DataStructName'))
            self.DataStruct.append(D)
            self.Tag.extend(D.get('Tag'))
            self.CaseName.extend([T.get('CaseName') for T in D.get('Tag')])
            self.DataSpecies.extend(D.get('DataSpecies'))
            # Adding extralabels (e.g. slice)
            if kwargs.get('ExtraLabels') is None:
                self.ExtraLabels.extend(D.get('ExtraLabels'))
            else:
                assert len(kwargs.get('ExtraLabels')) == len(D.get('ExtraLabels')),\
                    'ExtraLabels must be a list with number of elements = length of Data per DataStruct'
                self.ExtraLabels.extend(kwargs.get('ExtraLabels'))
            self.PrintVerbose('Adding data to plotter: DataStruct:{} with PlotDim:{}; AxisType:{}; DataSpecies:{}'
                              .format(D.get('DataName'), PlotDim, AxisType, D.get('DataSpecies')))

            assert PlotDim is not None and AxisType is not None, "PlotType and AxisType cannot be None"

            if self.PlotDim is not None:
                assert self.PlotDim == PlotDim, "Different PlotDim"
            else:
                self.PlotDim = PlotDim

            if self.AxisType is not None:
                assert self.AxisType == AxisType, "Different AxisType"
            else:
                self.AxisType = AxisType

            # Add data from datastruct to plotter
            if self.PlotDim == '1D':
                XData = D.get('XData')
                if XData is not None:
                    self.XData.extend(XData)
                else:
                    raise ValueError('Cannot find XData')

                YData = D.get('YData')
                if YData is not None:
                    self.YData.extend(YData)
                else:
                    raise ValueError('Cannot find YData')

            elif self.PlotDim == '2D':

                XData = D.get('XData')
                if XData is not None:
                    self.XData.extend(XData)
                else:
                    raise ValueError('Cannot find XData')

                YData = D.get('YData')
                if YData is not None:
                    self.YData.extend(YData)
                else:
                    raise ValueError('Cannot find YData')

                XYData = D.get('XYData')
                if XYData is not None:
                    self.XYData.extend(XYData)
                else:
                    raise ValueError('Cannot find XYData')

            else:
                raise ValueError('Unknown PlotType:', self.PlotDim)

        self.SetAxeSettings(**kwargs)

    def Plot(self, **kwargs):
        if self.PlotDim == '2D':
            for (X, Y, XY) in zip(self.XData, self.YData, self.XYData):
                self.PlotHandle.extend(self.PlotData2D(X, Y, XY, **kwargs))
        elif self.PlotDim == '1D':
            self.PlotHandle.extend(self.PlotData1D(self.XData, self.YData, self.Labels, **kwargs))

        # set ax properties
        for (k, v) in self.ax_settings.items():
            if hasattr(self.ax, 'set_{}'.format(k)):
                self.PrintVerbose('Applying set_{}({})'.format(k, v))
                getattr(self.ax, 'set_' + k)(v)

        # set artist properties
        self.SetLineProperties(**kwargs)
        self.SetLabel(**kwargs)
        self.SetLegend(**kwargs)


    def SetAxeSettings(self, **kwargs):
        # Axis labels
        if kwargs.get('xlabel') is None and self.AutoLabels:
            if 'r' in self.AxisType:
                self.ax_settings['xlabel'] = 'R'
            elif 'psi' in self.AxisType:
                self.ax_settings['xlabel'] = 'Psi'
            elif self.AxisType == 'ix':
                self.ax_settings['xlabel'] = 'ix'

        if kwargs.get('ylabel') is None and self.AutoLabels:
            if self.PlotDim == '1D':
                self.ax_settings['ylabel'] = self.DataName
            elif self.PlotDim == '2D':
                if self.AxisType == 'rz':
                    self.ax_settings['ylabel'] = 'Z'
                elif self.AxisType == 'ij':
                    self.ax_settings['ylabel'] = 'iy'

        # Units
        if self.ax_settings.get('xlabel') is not None:
            if kwargs.get('xunit') is None and self.AutoUnits:
                if self.AxisType == 'r' or self.AxisType == 'z' or self.AxisType == 'rz':
                    self.ax_settings['xlabel'] += ' [{}]'.format('m')
            if kwargs.get('xunit') is not None:
                self.ax_settings['xlabel'] += ' [{}]'.format(kwargs.get('xunit'))
        if self.ax_settings.get('ylabel') is not None:
            if kwargs.get('yunit') is None and self.AutoUnits:
                if self.AxisType == 'rz':
                    self.ax_settings['ylabel'] += ' [{}]'.format('m')
            if kwargs.get('yunit') is not None:
                self.ax_settings['ylabel'] += ' [{}]'.format(kwargs.get('yunit'))

        self.ax_settings.update(**kwargs)

    def PreparePlot1DData(self, XType=None, DimSplit=None):
        (DimSplit, XType) = self.GetDimSplit(XType, DimSplit, self.Data)

        self.PrintVerbose('Preparing 1D for for XType:{} ; DimSplit={}'.format(XType, DimSplit))
        DataSplit = self._SplitDataArray(self.Data, DimSplit)
        IndexesSplit = self._SplitIndexes(self.Indexes, DimSplit)
        # Now we get the grid for each Data

        DataOut = []
        XDataOut = []
        LabelOut = []
        for I, D in zip(IndexesSplit, DataSplit):
            XData = self.GetXData(self.Grid, XType, Indexes=I)
            XDataOut.append(XData.squeeze())
            DataOut.append(D.squeeze())
            if DimSplit is not None:
                LabelOut.append('_{}'.format(I[DimSplit]))
            else:
                LabelOut.append('')

        XDataOut = np.array(XDataOut).squeeze().transpose()
        DataOut = np.array(DataOut).squeeze().transpose()
        return (XDataOut, DataOut, LabelOut, XType)

    def Plotter1D(self, XType=None, DimSplit=None, **kwargs):

        (XDataOut, DataOut, LabelOut, XType) = self.PreparePlot1DData(XType, DimSplit)
        Labels = ['{} {}={}'.format(self.Label, XType, L) for L in LabelOut]
        self.PrintVerbose('Plot1D: XType:{},DataOut.shape:{} ; XDataOut.shape={}'.format(XType, DataOut.shape, XDataOut.shape))
        return self.PlotData1D(XDataOut, DataOut, Labels, **kwargs)

    def PreparePlot2DGrid(self, XType=None, **kwargs):
        if self.Grid is None:
            print('No grid available in plotter')
            return (None, None)
        if XType == 'ixiy':
            pass
        else:

            r = self.Grid.get('rm')
            z = self.Grid.get('zm')

            if self.zshift is not None:
                z = z + self.zshift
            if self.rshift is not None:
                r = r + self.rshift

            if z is None or r is None:
                return (None, None)
            else:
                r = self._SliceDataArray(r, self.Indexes[0:2])
                z = self._SliceDataArray(z, self.Indexes[0:2])
        return (r, z)

    def Plotter2D(self, **kwargs):

        (r, z) = self.PreparePlot2DGrid(**kwargs)
        if r is None or z is None:
            print('Problem with the grid in plotter. Grid:', self.Grid)
            return None
        else:
            PlotHandle = self.PlotData2D(r, z, self.Data, **kwargs)
            return PlotHandle

    def SetPlotLabel(self, PlotLabel=None, PlotLabelLocation: str or tuple = 'se', PlotLabelFontSize=10, **kwargs):
        if PlotLabel is None:
            PlotLabel = self.PlotLabel
        if self.ax is None:
            return

        Pos = dict(se=(1, 0), sw=(0, 0), nw=(0, 1), ne=(1, 1))

        if type(PlotLabelLocation) == str:
            PlotLabelLocation = Pos.get(PlotLabelLocation)
        PlotLabelLocation
        self.HandlePlotLabel = self.ax.text(PlotLabelLocation[0], PlotLabelLocation[1], PlotLabel, transform=self.ax.transAxes, fontsize=PlotLabelFontSize, verticalalignment='bottom', horizontalalignment='right')

    def SetYLabel(self, YLabel=None, YLabelFontSize=10, **kwargs):
        if YLabel is None:
            if self.YLabel is None:
                if self.PlotDim == '2D':
                    self.YLabel = 'R [m]'
        else:
            self.YLabel = YLabel

        self.ax.set_ylabel(self.YLabel, fontsize=YLabelFontSize)

    def SetPlotTitle(self, PlotTitle=None, TitleFontSize=10, **kwargs):
        if PlotTitle is None:
            if self.PlotTitle is not None:
                PlotTitle = self.PlotTitle
            else:
                return
        if self.ax is None:
            return
        else:
            self.ax.set_title(PlotTitle, fontsize=TitleFontSize)

            # self.ax.set_title('{}:({},{})'.format(self.Label,self.CompactStr(self.Indexes[0]),self.CompactStr(self.Indexes[1])))

    def GetAxProperties(self, Override=False):
        for P in self.AxProperties:
            Prop = getattr(self, P)
            if Prop is None:
                if self.ax is not None:
                    if hasattr(self.ax, 'get_' + P):
                        f = getattr(self.ax, 'get_' + P)
                        setattr(self, P, f())

    def SetupAx(self, Data, Label, ax=None, **kwargs):
        ax = self.GetAx(ax)
        Data = np.squeeze(Data)
        if kwargs.get('xlabel') is not None:
            ax.set_xlabel(kwargs.get('XLabel'))

    def SetGrid(self, Grid):
        self.Grid = Grid

    def SetSharedXAxis(self, ax):
        if not self.IsBottom:
            self.ax.set_xlabel(None)
            self.ax.xaxis.set_ticklabels([])
        if self.ax != ax:
            self.ax.get_shared_x_axes().join(self.ax, ax)
        # self.ax.set_xlim(ax.get_xlim())

    def SetSharedYAxis(self, ax):
        if not self.IsLeft:
            self.ax.set_ylabel(None)
            self.ax.yaxis.set_ticklabels([])
        if self.ax != ax:
            self.ax.get_shared_y_axes().join(self.ax, ax)


@AddPrintMethod(1)
class UBoxPlotFigure(UBoxDataParser):
    def __init__(self, FigName=None, Parent=None, **kwargs):
        if kwargs.get('Verbose') is not None:
            self.Verbose = kwargs.get('Verbose')
        self.DataPlotter = {}
        self.fig = plt.figure()
        self.Parent = Parent
        if FigName is not None:
            self.fig.canvas.set_window_title(self.MakeFigTitle(FigName))
        self.Name = self.fig.canvas.get_window_title()

        self.Print('new figure "{}" created'.format(self.Name))

    @property
    def Name(self):
        return self.__Name

    @Name.setter
    def Name(self, FigName):
        self.__Name = FigName
        self.fig.canvas.set_window_title(FigName)

    @staticmethod
    def SetNxNy(Nplot, Nrow=None, Ncol=None, **kwargs):
        if Nplot == 0:
            return (1, 1)

        Np = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        Nx = [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3]
        Ny = [1, 2, 3, 2, 3, 3, 4, 4, 5, 5, 4, 4]
        if Ncol is None and Nrow is not None and Nrow > 0:
            Ncol = int(np.ceil(Nplot / Nrow))
            return (Nrow, Ncol)
        elif Nrow is None and Ncol is not None and Ncol > 0:
            Nrow = int(np.ceil(Nplot / Ncol))
            return (Nrow, Ncol)
        elif Nrow is not None and Ncol is not None:
            if Nplot > Nrow * Ncol:
                raise IOError('Nplot>Nrow*Ncol')
            return (Nrow, Ncol)
        else:
            if Nplot > 12:
                raise IOError('Cannot plot more than 12 plots on the same figure... Type ResetPlot() to clear plot')
            else:
                return (Nx[Np.index(Nplot)], Ny[Np.index(Nplot)])

    @ClassInstanceMethod
    def Plot(self, DataFields=None, Reset=False, **kwargs):

        if kwargs.get('Verbose') is not None:
            self.Verbose = kwargs.get('Verbose')

        if Reset:
            self.ResetPlot()

        if DataFields is not None and DataFields != []:
            self.AddDataPlotter(DataFields, **kwargs)

        self.ShowPlot(**kwargs)


    @ClassInstanceMethod
    def FigLayout(self, Nplot, pad=0.5, **kwargs):

        (self.Nx, self.Ny) = self.SetNxNy(Nplot, **kwargs)
        # fig, axs = plt.subplots(Nx, Ny, sharex='col', sharey='row',
        #                 gridspec_kw={'hspace': 0, 'wspace': 0})
        axs = self.fig.subplots(self.Nx, self.Ny)

        if type(axs) != np.ndarray:
            axs = np.array([axs])
        # =[]
        for ax in axs.flat:
            pass
            # ax.set_visible(False)
            # divider = make_axes_locatable(ax)
            # caxs.append(divider.append_axes('right', size='10%', pad=0.6))
        # axs = ImageGrid(fig, 111,          # as in plt.subplot(111)
        #          nrows_ncols=(self.Nx,self.Ny),direction='column',
        #          axes_pad=0.10,
        #          share_all=True,
        #          cbar_location="right",
        #          cbar_mode="each",
        #          cbar_size="7%",
        #          cbar_pad=0.15,
        #          label_mode='1',
        #          cbar_set_cax=True
        #          )

        return axs

    def SetAspect(self, *args):
        for Plotter in self.DataPlot.values():
            if Plotter.ax is not None:
                Plotter.ax.set_aspect(*args)
                # ,adjustable='datalim'

    @ClassInstanceMethod
    def ShareAxis(self, Axis='xy', PlotDim='2D'):
        Plotter = [P for P in self.DataPlotter.values() if P.PlotDim == PlotDim]
        axesPlotter = [P.ax for P in Plotter]
        if (len(axesPlotter)) > 0:
            for P in Plotter:
                if 'x' in Axis.lower():
                    P.SetSharedXAxis(axesPlotter[0])

                if 'y' in Axis.lower():
                    P.SetSharedYAxis(axesPlotter[0])
                    P.ax.set_ylim(axesPlotter[0].get_ylim())
                    if not P.IsLeft:
                        P.ax.set_ylabel(None)
                        plt.setp(P.ax.get_yticklabels(), visible=False)

    @ClassInstanceMethod
    def ShareCLim(self, **kwargs):
        Plotter = [P for P in self.DataPlotter.values() if P.PlotDim == '2D']
        axesPlotter = [P.ax for P in Plotter]

        clow = np.array([p.get_clim()[0] for P in Plotter for p in P.PlotHandle if hasattr(p, 'get_clim')])
        chigh = np.array([p.get_clim()[1] for P in Plotter for p in P.PlotHandle if hasattr(p, 'get_clim')])
        if len(clow) > 0 and len(chigh) > 0:
            cmin = min(clow)
            cmax = max(chigh)
            [p.set_clim([cmin, cmax]) for P in Plotter for p in P.PlotHandle if hasattr(p, 'set_clim')]

    @ClassInstanceMethod
    def LinkAxis(self, LinkAxis='xy', LinkDim='all', ShareCLim=True, **kwargs):
        self.PrintVerbose('LinkAxis:', LinkAxis)
        if LinkDim is None or LinkDim.lower() == 'no':
            pass
        elif LinkDim == 'all':
            self.ShareAxis(LinkAxis, PlotDim='1D')
            self.ShareAxis(LinkAxis, PlotDim='2D')
        elif LinkDim == '1D':
            self.ShareAxis(LinkAxis, PlotDim='1D')
        elif LinkDim == '2D':
            self.ShareAxis(LinkAxis, PlotDim='2D')
        else:
            raise KeyError('LikeDim must be: "all", "1D" or "2D" or "no"/None')
        if ShareCLim:
            self.ShareCLim(**kwargs)

    @staticmethod
    def IsBottom(i, Nx, Ny):
        if int(np.ceil(i / Ny)) == Nx:
            return True
        else:
            return False

    @staticmethod
    def IsLeft(i, Nx, Ny):
        if np.mod(i, Ny) == 0:
            return True
        else:
            return False

    @ClassInstanceMethod
    def ShowPlot(self, TightLayout=True, **kwargs):
        Nplot = len(list(self.DataPlotter.keys()))
        self.axs = self.FigLayout(Nplot, **kwargs)
        count = 1
        if TightLayout:
            plt.tight_layout()
        for (Name, Plotter), ax in zip(self.DataPlotter.items(), self.axs.flat):
            Plotter.ax = ax
            Plotter.IsBottom = self.IsBottom(count, self.Nx, self.Ny)
            Plotter.IsLeft = self.IsLeft(count, self.Nx, self.Ny)
            Plotter.Plot(**kwargs)
            count += 1
        self.LinkAxis(**kwargs)


        plt.show()

    @ClassInstanceMethod
    def AddDataPlotter(self, DataFields=[], DataType='UEDGE', Refresh=False, GroupBy=None, Fig=None, **kwargs):
        if kwargs.get('CompareWith') is not None:
            kwargs.get('CompareWith')

        if kwargs.get('Verbose') is not None:
            self.Verbose = kwargs.get('Verbose')
        else:
            self.Verbose = self.Parent.Verbose

        # Check the grid
        if kwargs.get('Grid') is not None:
            Grid = kwargs.pop('Grid')
        else:
            Grid = None

        if Grid is None:
            if hasattr(self.Parent, 'GetGrid'):
                Grid = self.Parent.GetGrid()
        elif type(Grid) == str:
            print('Read grid file: ',Grid)
            Grid = UBoxGrid.ReadGridFile(Grid)

        if kwargs.get('Tag') is not None:
            Tag = kwargs.pop('Tag')
        else:
            Tag = None

        if Tag is None:
            if hasattr(self.Parent, 'GetTag'):
                Tag = self.Parent.GetTag()
            else:
                Tag = {}

        # Process and add data for plots
        DicData = self.Parent.ParseDataFields(DataFields, DataType=DataType, **kwargs)

        self.ProcessPlotterData(DicData, Grid, Tag, **kwargs)

        # Create Plot Object based on grouping setting
        FirstData = None
        for DataStruct in DicData.values():
            DataName = DataStruct['DataName']
            DataStructName = DataStruct['DataStructName']
            self.PrintVerbose('Making plotter for {} / {} with GroupBy:{}'.format(DataName, DataStructName, GroupBy))

            if GroupBy is None or GroupBy.lower() == 'single' or GroupBy.lower() == 'no' or DataStruct['PlotDim'] == '2D':
                if self.DataPlotter.get(DataStructName) is not None and not Refresh:
                    i = 1
                    while self.DataPlotter.get(DataStructName) is not None:
                        DataStructName = DataStructName + '_#' + str(i)
                        i = i + 1
                    DataStruct['DataStructName'] = DataStructName
                self.DataPlotter[DataStructName] = UBoxDataPlotter(DataStruct, **kwargs)

            elif GroupBy.lower() == 'name':
                if self.DataPlotter.get(DataName) is not None:
                    self.PrintVerbose('Adding {} to exiting plotter {}'.format(DataStructName, DataName))
                    self.DataPlotter[DataName].AddPlotData(DataStruct, **kwargs)
                else:
                    self.DataPlotter[DataName] = UBoxDataPlotter(DataStruct, **kwargs)

            elif GroupBy.lower() == 'new':
                if FirstData is None:
                    self.DataPlotter[DataName] = UBoxDataPlotter(DataStruct, **kwargs)
                    FirstData = DataName
                else:
                    self.DataPlotter[FirstData].AddPlotData(DataStruct, **kwargs)

            else:
                raise ValueError('Unknow option for GroupBy')
            # set verbose mode of plotters
            for DP in self.DataPlotter.values():
                DP.Verbose = self.Verbose

    def ProcessPlotterData(self, DicData, Grid, Tag, PlotType='auto', **kwargs):
        for DataName, DataStruct in DicData.items():
            DataStruct['DataName'] = DataName.split('__')[0]
            DataStruct['DataStructName'] = DataName
            if DataName.count('__') > 0:
                DataSpecies = DataName.split('__')[-1]
            else:
                DataSpecies = '0'
            if Grid is None:
                continue
            else:
                DataStruct['Grid'] = Grid

            Data = DataStruct.get('Data')
            if Data is None:
                continue

            Indexes = DataStruct.get('Indexes')
            if Indexes is None:
                continue

            (PlotDim, AxisType) = self.SetPlotType(Data, PlotType)

            DataStruct['PlotDim'] = PlotDim
            DataStruct['AxisType'] = AxisType

            self.PrintVerbose('ProcessPlotterData: DataStructName={}; PlotDim={}; AxisType={}'.format(DataName,PlotDim,AxisType))

            if PlotDim == '1D':
                DataStruct.update(self.MakePlotData1D(Data, Indexes, Grid, AxisType, **kwargs))
            elif PlotDim == '2D':
                DataStruct.update(self.MakePlotData2D(Data, Indexes, Grid, AxisType, **kwargs))
            else:
                raise ValueError('Unknown PlotDim:"{}"'.format(PlotDim))
            DataStruct['DataSpecies'] = [DataSpecies for X in DataStruct['XData']]
            DataStruct['Tag'] = [Tag for X in DataStruct['XData']]
    @staticmethod
    def SetPlotType(Data, PlotType='auto'):

        if Data is None:
            raise ValueError('Data cannot be none')
        elif type(Data) != np.ndarray:
            raise ValueError('Data for Plotter must be a numpy array')
        elif len(Data.shape) > 2 and Data.shape[2] > 1:
            raise ValueError('Plotter object cannot contain arrays of dimension>2')

        DataDim = len(np.squeeze(Data).shape)
        PlotType = PlotType.strip()
        if PlotType.lower() == 'auto':
            if DataDim == 1:
                PlotDim = '1D'
                AxisType = 'r'
            else:
                PlotDim = '2D'
                AxisType = 'rz'

        elif PlotType.strip().lower() in ['r', 'z', 'psi', 'p', 'ix', 'iy']:
            PlotDim = '1D'
            AxisType = PlotType.lower()

        elif PlotType.strip().lower() in ['ij', 'rz']:
            if DataDim < 2:
                raise ValueError('2D plot requested for data array of dimension <2')
            else:
                PlotDim = '2D'
                AxisType = Type.lower()
        else:
            raise ValueError('PlotType:"{}". Type of plot must be: auto,rz,ij,r, z, psi, p, ix, iy'.format(PlotType))

        return (PlotDim, AxisType)

    @staticmethod
    def GetDimSplit(AxisType):
        if AxisType in ['r', 'psi', 'iy']:
            DimSplit = 0
        elif AxisType in ['ix', 'p', 'z']:
            DimSplit = 1
        else:
            raise ValueError('AxisType:{}. AxisType must be of type: r,z,psi,ix,iy,p')
        return DimSplit

    def GetXData(self, Grid, AxisType, Indexes=None, CellPt=0, rshift=0.0, zshift=0.0, psishift=0.0, **kwargs):

        assert(Grid is not None)
        if Grid.get('rm') is None or Grid.get('zm') is None or Grid.get('psi') is None:
            raise ValueError('Cannot find rm or zm or psi in Grid Dic')

        if AxisType == 'ix':
            XData = np.indices(Grid['rm'].shape)[0]

        elif AxisType == 'iy':
            XData = np.indices(Grid['rm'].shape)[1]

        elif AxisType == 'r':
            XData = Grid['rm'] + rshift

        elif AxisType in ['p', 'z']:
            XData = Grid['zm'] + zshift

        elif AxisType == 'psi':
            if Grid.get('psinorm') is not None:
        
                XData = Grid['psinorm'] + psishift
            elif Grid.get('psinc') is not None:
                XData = Grid['psinc'] + psishift
            else:
                XData = Grid['psi'] + psishift
                print('>>>>>>>>>>>>>> psi')
        else:
            raise ValueError('Unknown AxisType')

        if Indexes is not None:
            XData = self._SliceDataArray(XData, Indexes[0:2])
            XData = XData[..., CellPt]

        return np.squeeze(XData)

    def GetXYData(self, Grid, AxisType, Indexes, rshift=0.0, zshift=0.0, **kwargs):
        if AxisType == 'ixiy':
            XData = np.indices(Grid['rm'].shape)[0]
            YData = np.indices(Grid['zm'].shape)[1]
        elif AxisType == 'rz':
            r = Grid.get('rm')
            z = Grid.get('zm')
            XData = self._SliceDataArray(r, Indexes[0:2])
            YData = self._SliceDataArray(z, Indexes[0:2])
        else:
            raise ValueError('Unknown AxisType for 2D data:{}', AxisType)
        return (XData, YData)

    def MakePlotData1D(self, Data, Indexes, Grid, AxisType, **kwargs):
        DimSplit = self.GetDimSplit(AxisType)
        DataSplit = self._SplitDataArray(Data, DimSplit)
        IndexesSplit = self._SplitIndexes(Indexes, DimSplit)
        self.PrintVerbose('Preparing 1D for for XType:{} ; DimSplit={}'.format(AxisType, DimSplit))

        DataOut = []
        XDataOut = []
        LabelOut = []
        for I, D in zip(IndexesSplit, DataSplit):
            XData = self.GetXData(Grid, AxisType, Indexes=I, **kwargs)
            XDataOut.append(XData.squeeze())
            DataOut.append(D.squeeze())
            if DimSplit is not None:
                if AxisType in ['r', 'psi', 'iy']:
                    Str = 'ix'
                else:
                    Str = 'iy'
                LabelOut.append('_{}={}'.format(Str, I[DimSplit]))
            else:
                LabelOut.append('')

        # XDataOut=np.array(XDataOut).squeeze().transpose()
        # DataOut=np.array(DataOut).squeeze().transpose()
        return {'XData': XDataOut, 'YData': DataOut, 'ExtraLabels': LabelOut}

    def MakePlotData2D(self, Data, Indexes, Grid, AxisType, **kwargs):
        (XData, YData) = self.GetXYData(Grid, AxisType, Indexes, **kwargs)
        self.PrintVerbose('MakePlotData2D: AxisType:{} XData.shape={}; YData.Shape:{}'.format(AxisType,XData.shape,YData.shape))
        return {'XData': [XData], 'YData': [YData], 'XYData': [Data], 'ExtraLabels': [""]}

    @ClassInstanceMethod
    def MakeFigTitle(self,TitlePart=['CaseName']):
        Title=[]
        if type(TitlePart) == list:
            for T in TitlePart:
                if T == 'CaseName':
                    if hasattr(self.Parent,'Tag'):
                        CaseName = self.Parent.Tag.get('CaseName')
                    else:
                        if hasattr(self.Parent,'GetTag'):
                            CaseName = self.Parent.GetTag().get('CaseName')
                        else:
                            CaseName = ""
                    Title.append(CaseName)
                elif T == 'Project':
                    if hasattr(self.Parent,'Tag'):
                        Project = self.Parent.Tag.get('Project').get('Name')
                    else:
                        if hasattr(self.Parent,'GetTag'):
                            Project = self.Parent.GetTag().get('Project').get('Name')
                        else:
                            Project = ""
                    Title.append(Project)
                else:
                    if type(T) == list:
                        Title.extend(T)
                    else:
                        Title.append(T)
            return ' | '.join(Title)

        else:
            return TitlePart
@AddPrintMethod(0)
class UBoxPlot(UBoxDataParser):

    def __init__(self):
        self.CurrentFigure = None
        self.Figures = {}

    def NewFig(self, FigName=None, **kwargs):
        if not hasattr(self, 'CurrentFigure'):
            self.CurrentFigure = None
        if not hasattr(self, 'Figures'):
            self.Figures = {}

        Fig = UBoxPlotFigure(Parent=self, FigName=FigName, **kwargs)
        if self.Figures.get(Fig.Name) is not None:
            Fig.Name += '#1'
        self.Figures[Fig.Name] = Fig
        self.CurrentFigure = self.Figures[Fig.Name]

    @ClassInstanceMethod
    def Plot(self, DataFields=None, NewFig=True, FigName=None, **kwargs):
        if kwargs.get('Verbose') is not None:
            self.Verbose = kwargs.get('Verbose')

        if not hasattr(self, 'CurrentFigure'):
            self.CurrentFigure = None
        if not hasattr(self, 'Figures'):
            self.Figures = {}

        if self.CurrentFigure is None or NewFig:
            self.NewFig(FigName)

        if FigName is not None:
            self.CurrentFigure = self.Figures.get(FigName)


        if kwargs.get('CompareWith') is not None:
            self.SetDefaultCompareWithKwargs(kwargs)
            CompareWith=kwargs.get('CompareWith')
            if type(CompareWith) != list:
                CompareWith=[CompareWith]
            self.PrintVerbose('Add plot for comparison with:',CompareWith)

            for W in CompareWith:
                    Parent = self.CurrentFigure.Parent
                    try:
                        self.CurrentFigure.Parent = W
                        self.CurrentFigure.AddDataPlotter(DataFields, **kwargs)
                    except Exception:
                        raise Exception
                    finally:
                        self.CurrentFigure.Parent = Parent
        self.CurrentFigure.Plot(DataFields, **kwargs)

    @ClassInstanceMethod
    def SetDefaultCompareWithKwargs(self, kwargs):
        if kwargs.get('CompareWith') is not None:
            if kwargs.get('GroupBy') is None:
                    kwargs['GroupBy'] = 'Name'

            if kwargs.get('SetupLabels') is None:
                kwargs['SetupLabels'] = ['CaseName']
            else:
                if type(kwargs.get('SetupLabels')) != list:
                    kwargs['SetupLabels'] = [kwargs.get('SetupLabels')]
                kwargs['SetupLabels'].append('CaseName')
            if kwargs.get('color') is None:
                kwargs['color'] = {'DataSpecies':'default'}

            if kwargs.get('linestyle') is None:
                kwargs['linestyle'] = {'CaseName':'default'}

    @ClassInstanceMethod
    def AddPlot(self, DataFields=None, NewFig=False, FigName=None, **kwargs):
        if kwargs.get('Verbose') is not None:
            self.Verbose = kwargs.get('Verbose')

        self.Print('Adding plot:{}'.format(DataFields))

        if not hasattr(self, 'CurrentFigure'):
            self.CurrentFigure = None
        if not hasattr(self, 'Figures'):
            self.Figures = {}

        if self.CurrentFigure is None or NewFig:
            self.NewFig(FigName)

        if FigName is not None and self.Figures.get(FigName) is not None:
            self.CurrentFigure = self.Figures.get(FigName)


        if kwargs.get('CompareWith') is not None:
            self.SetDefaultCompareWithKwargs(kwargs)
            CompareWith = kwargs.get('CompareWith')
            if type(CompareWith) != list:
                CompareWith=[CompareWith]
            self.PrintVerbose('Add plot for comparison with:',CompareWith)
            for W in CompareWith:
                    Parent = self.CurrentFigure.Parent
                    try:
                        self.CurrentFigure.Parent = W
                        self.CurrentFigure.AddDataPlotter(DataFields, **kwargs)
                    except Exception:
                        raise Exception
                    finally:
                        self.CurrentFigure.Parent = Parent

        self.CurrentFigure.AddDataPlotter(DataFields, **kwargs)


    @ClassInstanceMethod
    def ShowPlot(self, FigName=None, **kwargs):
        self.Print('Show plot')
        if not hasattr(self, 'CurrentFigure'):
            self.CurrentFigure = None
        if not hasattr(self, 'Figures'):
            self.Figures = {}

        if FigName is not None and self.Figures.get(FigName) is not None:
            self.CurrentFigure = self.Figures.get(FigName)


        self.SetDefaultCompareWithKwargs(kwargs)

        if self.CurrentFigure is not None:
            self.CurrentFigure.ShowPlot(**kwargs)

    def Clear(self, FigName=None, **kwargs):

        if FigName is not None and self.Figures.get(FigName) is not None:
            self.CurrentFigure = self.Figures.get(FigName)
        if self.CurrentFigure is not None:
            self.CurrentFigure.Clear()

    def Close(self, FigName=None):
        if FigName is not None and self.Figures.get(FigName) is not None:
            self.CurrentFigure = self.Figures.get(FigName)

        if self.CurrentFigure is not None:
            CF = self.Figures.pop(self.CurrentFigure.Name)
            plt.close(CF.fig)
            L = list(self.Figures.keys())
            if len(L) > 0:
                self.CurrentFigure = self.Figures(L[-1])
            else:
                self.CurrentFigure = None

    def CloseAll(self):
        for p in self.Figures.keys():
            CF = self.Figures.pop(p)
            plt.close(CF.fig)
        self.CurrentFigure = None

    def CloseAll(self):
        for p in list(self.Figures.keys()):
            CF = self.Figures.pop(p)
            plt.close(CF.fig)
        self.CurrentFigure = None

    @ClassInstanceMethod
    def NewFigure(self):
        self.DataPlot = {}
        self.fig = None

    @ClassInstanceMethod
    def AddRadialPlot(self, DataFields=None, Location='Outer', ShowGuardCell=False, **kwargs):
        if type(Location) != list:
            Location = [Location]
        IdxSlice = []
        for L in Location:
            if L == 'Outer':
                IdxSlice.append(-2)
            elif L == 'Inner':
                IdxSlice.append(1)
            else:
                if type(L) == list:
                    IdxSlice.extend(L)
                else:
                    IdxSlice.append(L)
        IdxSlice = [IdxSlice]
        DimSlice = [0]

        if not ShowGuardCell:
            DimSlice.append(1)
            IdxSlice.append((1, -1))

        if kwargs.get('PlotType') is None:
            kwargs['PlotType'] = 'r'
        assert kwargs['PlotType'].lower() in ['r', 'ix', 'psi'], 'For radial plot, PlotType is either "r", "i" or "psi"'
        self.AddPlot(DataFields, IdxSlice=IdxSlice, DimSlice=DimSlice, **kwargs)


    @ClassInstanceMethod
    def DivertorPlot(self, DataFields=None, ShowGuardCell=False, **kwargs):
        if kwargs.get('Location') is None:
            kwargs['Location'] = ['Inner', 'Outer']
        if kwargs.get('PlotType') is None:
            kwargs['PlotType'] = 'psi'
        if kwargs.get('LinkAxis') is None:
            kwargs['LinkAxis'] = 'x'
        if kwargs.get('GroupBy') is None:
            kwargs['GroupBy'] = 'Name'

        Loc = kwargs['Location']
        self.NewFig(['Project', 'CaseName', Loc])

        if DataFields is None:
            self.AddRadialPlot(['te'], **kwargs)
            self.AddRadialPlot(['ti'], **kwargs)
            self.AddRadialPlot(['ni'], **kwargs)
            self.AddRadialPlot(['ng'], **kwargs)
            self.AddRadialPlot(['phi'], **kwargs)
            self.AddRadialPlot(['ne'], **kwargs)

        self.ShowPlot(**kwargs)

        # if not Replot:
        #     if DataFields is not None and DataFields!=[]:
        #         self.ResetPlot()
        #     else:
        #         raise IOError('Cannot reset DataPlot when no data fields are given')

    # @ClassInstanceMethod
    # def PreparePlotter(self, DicData, Grid, Tag, NameDataPlot, NameData, **kwargs):
    #     DicPlotter = DicData
    #     DicPlotter['Grid'] = Grid
    #     DicPlotter['Tag'] = Tag
    #     DicPlotter['NameData'] = NameData
    #     DicPlotter['NameDataPlot'] = NameDataPlot
    #     DicPlotter.update(kwargs)

    #     if kwargs.get('PlotLabel') is None:
    #         DicPlotter['PlotLabel'] = NameData

    #     if kwargs.get('PlotTitle') is None:
    #         ProjectName = Tag.get('Project').get('Name')
    #         CaseName = Tag.get('CaseName')
    #         PlotTitle = []
    #         if ProjectName is not None:
    #             PlotTitle.append(ProjectName)
    #         if CaseName is not None:
    #             PlotTitle.append(CaseName)
    #         if PlotTitle != []:
    #             #print(PlotTitle)
    #             DicPlotter['PlotTitle'] = ':'.join(PlotTitle)

    #     return DicPlotter