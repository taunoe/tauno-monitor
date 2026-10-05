python = import('python').find_installation('python3')

test(
  'unit',
  python,
  args: ['-m', 'unittest', 'discover', '-s', meson.project_source_root() / 'tests'],
  workdir: meson.project_source_root(),
)
