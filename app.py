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

aboutText = """<p>User friendly guy for managing streams and playing them with VLC</p>"""

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
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)
        
        self.statusbar = self.CreateStatusBar()

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        
        m_text = wx.StaticText(panel, -1, "Favorite Channels")
        m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        m_text.SetSize(m_text.GetBestSize())
        box.Add(m_text, 0, wx.ALL, 10)
        
        #m_close = wx.Button(panel, wx.ID_CLOSE, "Close")
        #m_close.Bind(wx.EVT_BUTTON, self.OnClose)
        #box.Add(m_close, 0, wx.ALL, 10)
        
        # bMap = self.scale_bitmap(wx.Bitmap("images/top_channel_hd.png", wx.BITMAP_TYPE_ANY), 80, 50)
        # sBitMap = wx.StaticBitmap(panel, -1, bMap, (0, 0), (100, 50))
        # sBitMap.Bind(wx.EVT_MOUSE_EVENTS, self.OnPlay)
        #
        # box.Add(sBitMap, 0, wx.ALL, 10)
        self.LoadFavorites(panel, box)

        panel.SetSizer(box)
        panel.Layout()


    def LoadFavorites(self, panel, box):
        for key in streams:
            if not int(streams[key]['favorite']):
                continue
            img_name = 'images/%s.png' % key
            img = img_name if os.path.isfile(img_name) else 'images/no_image.png'
            bMap = self.scale_bitmap(wx.Bitmap(img, wx.BITMAP_TYPE_ANY), 80, 50)
            sBitMap = wx.StaticBitmap(panel, -1, bMap, (0, 0), (100, 50))
            sBitMap.Bind(wx.EVT_MOUSE_EVENTS, self.OnPlay)
            sBitMap.Bind(wx.EVT_MOUSE_EVENTS, lambda evt, temp=key: self.OnPlay(evt, temp))
            box.Add(sBitMap, 0, wx.ALL, 10)

    def OnClose(self, event):
        dlg = wx.MessageDialog(self, 
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        #result = dlg.ShowModal()
        #dlg.Destroy()
        #if result == wx.ID_OK:
        #    self.Destroy()
        self.Destroy()



    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()  
    
    def OnPlay(self, event, stream_id):
        if event.EventType != 10021:
            return

        #print streams[stream_id]['url']
        # call("vlc %s" % streams[stream_id]['url'], shell=True)
        p = subprocess.Popen("vlc --fullscreen %s" % streams[stream_id]['url'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def scale_bitmap(self, bitmap, width, height):
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

app = wx.App(redirect=True)   # Error messages go to popup window
LoadStreams()
top = Frame("Streamy")
top.Show()
app.MainLoop()
