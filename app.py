#!/usr/bin/python
# -*- coding: <<encoding>> -*-
#-------------------------------------------------------------------------------
#   <<project>>
# 
#-------------------------------------------------------------------------------

import wxversion
wxversion.select("2.8")
import wx, wx.html
import sys, re
import subprocess
import os.path
import  wx.lib.scrolledpanel as scrolled

aboutText = """<p>User friendly GUI for managing streams and playing them with VLC</p>"""

streams={}
def LoadStreams():
    stream_str = open('streams', 'r').read()
    streams_all = stream_str.split('\n')

    for streamLine in streams_all:
        if len(streamLine.strip()) == 0:
            continue
        if '://' not in streamLine:
            resplit = re.findall('\[[^\]]*\]|\([^\)]*\)|\"[^\"]*\"|\S+',streamLine)
            curren_id = resplit[0]
            streams[curren_id] = {'name': resplit[1].strip('"'), 'favorite': resplit[2], 'url':''}
        else:
            streams[curren_id]['url'] = streamLine


class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())
        
class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About Streamy",
            style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400,200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

class Frame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(350,600))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()

        m_streams = menu.Append(wx.ID_ANY, "&Show streams", "Show the list of stream URLs")
        self.Bind(wx.EVT_MENU, self.OnShowStreams, m_streams )

        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)

        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)


        topPanel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        search_btn = wx.SearchCtrl(topPanel, size=(200,-1), style=wx.TE_PROCESS_ENTER)
        search_btn.ShowSearchButton(1)
        search_btn.ShowCancelButton(1)
        search_btn.SetMenu(self.MakeMenu())
        box.Add(search_btn, 0, wx.EXPAND|wx.ALL, 10)

        # box = wx.FlexGridSizer(rows=4, cols=1, hgap=5, vgap=5)
        search_panel = scrolled.ScrolledPanel(topPanel, size=(20,50))
        search_box = wx.BoxSizer(wx.VERTICAL)
        #box = wx.FlexGridSizer(rows=2, cols=1, hgap=5, vgap=5)


        m_text = wx.StaticText(topPanel, -1, "Channels")
        m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        m_text.SetSize(m_text.GetBestSize())
        box.Add(m_text, 0, wx.ALL, 10)
        #box.Add(m_text, 0, wx.EXPAND)



        search_panel.SetSizer(search_box)
        search_panel.Layout()
        search_panel.SetupScrolling()

        #box.Add(search_panel, 0, wx.ALL, 10)
        box.Add(search_panel,0,wx.EXPAND|wx.ALL,border=10)

        favorite_panel = scrolled.ScrolledPanel(topPanel)
        favorite_box = wx.BoxSizer(wx.VERTICAL)
        favorite_panel.Bind(wx.EVT_SIZE, lambda evt, temp=favorite_box: self.OnSize(evt, temp))

        m_text2 = wx.StaticText(topPanel, -1, "Favorite")
        m_text2.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        m_text2.SetSize(m_text2.GetBestSize())
        box.Add(m_text2, 0, wx.ALL, 10)

        self.LoadFavorites(favorite_panel, favorite_box)

        favorite_panel.SetSizer(favorite_box)
        favorite_panel.Layout()
        favorite_panel.SetupScrolling()

        # box.Add(favorite_panel,0,wx.EXPAND|wx.ALL,border=10)
        box.Add(favorite_panel, 1, wx.EXPAND|wx.ALL,border=10)

        topPanel.SetSizer(box)
        topPanel.Layout()

    def LoadFavorites(self, panel, box):
        for key in streams:
            if not int(streams[key]['favorite']):
                continue
            img_name = 'images/%s.png' % key
            img = img_name if os.path.isfile(img_name) else 'images/no_image.png'
            bMap = self.scale_bitmap(wx.Bitmap(img, wx.BITMAP_TYPE_ANY), 80, 50)
            bmp = wx.BitmapButton(panel,-1,bMap)
            bmp.Bind(wx.EVT_BUTTON, lambda evt, temp=key: self.OnPlay(evt, temp))
            box.Add(bmp, 0, wx.ALL, 10)
            # box.Add(sBitMap, 0, wx.ALL, 10)
            # box.Add(sBitMap, 0, wx.EXPAND)

    def OnClose(self, event):
        self.Destroy()


    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()  

    def OnSize(self, event, box):
        width, height = self.GetClientSizeTuple()
        pass

    def OnShowStreams(self, event):
        all = ''
        for key in streams:
            all += streams[key]['name'] + ': ' + streams[key]['url'] + '\n\n'
        print all

    def OnPlay(self, event, stream_id):
        #print streams[stream_id]['url']
        # call("vlc %s" % streams[stream_id]['url'], shell=True)
        p = subprocess.Popen("vlc --fullscreen %s" % streams[stream_id]['url'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def scale_bitmap(self, bitmap, width, height):
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

    def MakeMenu(self):
        menu = wx.Menu()
        item = menu.Append(-1, "Recent Searches")
        item.Enable(False)
        for txt in [ "You can maintain",
                     "a list of old",
                     "search strings here",
                     "and bind EVT_MENU to",
                     "catch their selections" ]:
            menu.Append(-1, txt)
        return menu

app = wx.App(redirect=True)   # Error messages go to popup window
LoadStreams()
top = Frame("Streamy")
top.Show()
app.MainLoop()
