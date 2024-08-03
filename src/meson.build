pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'tauno_monitor'
gnome = import('gnome')

gnome.compile_resources('tauno-monitor',
  'tauno-monitor.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'tauno-monitor.in',
  output: 'tauno-monitor',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

tauno_monitor_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'tauno_serial.py',
  'tauno_logging.py',
  'guide.py',
  'preferences.py'
]

install_data(tauno_monitor_sources, install_dir: moduledir)
