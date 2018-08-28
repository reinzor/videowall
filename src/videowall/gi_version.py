import gi

gi.require_version('GLib', '2.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstNet', '1.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import GLib, Gst, GstNet, GObject, Gdk, Gtk
from gi.repository import GdkX11, GstVideo  # For window.get_xid(), xvimagesink.set_window_handle()

_ = Gst, GstNet, GObject, GLib, Gdk, Gtk, GdkX11, GstVideo
