application_id = 'art.taunoerik.tauno-monitor'

scalable_dir = 'hicolor' / 'scalable' / 'apps'
install_data(
  scalable_dir / ('@0@.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / scalable_dir
)

symbolic_dir = 'hicolor' / 'symbolic' / 'apps'
install_data(
  symbolic_dir / ('@0@-symbolic.svg').format(application_id),
  install_dir: get_option('datadir') / 'icons' / symbolic_dir
)

action_dir = join_paths('hicolor', 'scalable', 'actions')
action_icons = [
  join_paths(action_dir, 'update-symbolic.svg'),
  join_paths(action_dir, 'larger-brush-symbolic.svg'),
  join_paths(action_dir, 'search-folder-symbolic.svg'),
  join_paths(action_dir, 'arrow-circular-small-top-left-symbolic.svg'),
  join_paths(action_dir, 'dock-right-symbolic.svg'),
  join_paths(action_dir, 'scanner-symbolic.svg'),
  join_paths(action_dir, 'mouse-click-symbolic.svg'),
  join_paths(action_dir, 'paper-plane-symbolic.svg'),
  join_paths(action_dir, 'play-large-symbolic.svg'),
  join_paths(action_dir, 'stop-large-symbolic.svg'),
  ]
install_data(
  action_icons,
  install_dir: join_paths(get_option('datadir'), 'icons', action_dir)
)