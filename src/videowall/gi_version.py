import gi

gi.require_version('GLib', '2.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstNet', '1.0')

from gi.repository import GLib, Gst, GstNet, GObject

_ = Gst, GstNet, GObject, GLib
