pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'taunomonitor'
gnome = import('gnome')

gnome.compile_resources('taunomonitor',
  'taunomonitor.gresource.xml',
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
  input: 'taunomonitor.in',
  output: 'taunomonitor',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

taunomonitor_sources = [
  '__init__.py',
  'main.py',
  'window.py',
]

install_data(taunomonitor_sources, install_dir: moduledir)
