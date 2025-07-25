"""
命令行接口
Command Line Interface for HumanMouse
"""
import argparse
import sys
from typing import Optional
from .__version__ import __version__
from .controllers.mouse_controller import HumanMouseController


def main(argv: Optional[list] = None) -> int:
    """
    主命令行入口
    Main command line entry point
    """
    parser = argparse.ArgumentParser(
        prog='humanmouse',
        description='Human-like mouse movement automation tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Move mouse from current position to (800, 600)
  humanmouse move --to 800 600
  
  # Move and click at position
  humanmouse click --at 500 400
  
  # Drag from one position to another
  humanmouse drag --from 100 100 --to 800 600
  
  # Set custom speed
  humanmouse move --to 800 600 --speed 2.0
        """
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    # 创建子命令
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )
    
    # move 命令
    move_parser = subparsers.add_parser(
        'move',
        help='Move mouse to position'
    )
    move_parser.add_argument(
        '--to',
        nargs=2,
        type=int,
        required=True,
        metavar=('X', 'Y'),
        help='Target position (x y)'
    )
    move_parser.add_argument(
        '--speed',
        type=float,
        default=1.0,
        help='Speed factor (default: 1.0)'
    )
    
    # click 命令
    click_parser = subparsers.add_parser(
        'click',
        help='Move and click at position'
    )
    click_parser.add_argument(
        '--at',
        nargs=2,
        type=int,
        required=True,
        metavar=('X', 'Y'),
        help='Click position (x y)'
    )
    click_parser.add_argument(
        '--button',
        choices=['left', 'right', 'middle'],
        default='left',
        help='Mouse button (default: left)'
    )
    click_parser.add_argument(
        '--double',
        action='store_true',
        help='Double click'
    )
    
    # drag 命令
    drag_parser = subparsers.add_parser(
        'drag',
        help='Drag from one position to another'
    )
    drag_parser.add_argument(
        '--from',
        nargs=2,
        type=int,
        required=True,
        metavar=('X', 'Y'),
        help='Start position (x y)'
    )
    drag_parser.add_argument(
        '--to',
        nargs=2,
        type=int,
        required=True,
        metavar=('X', 'Y'),
        help='End position (x y)'
    )
    
    # 解析参数
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # 创建控制器
        controller = HumanMouseController()
        
        # 获取当前鼠标位置
        import pyautogui
        current_pos = pyautogui.position()
        
        # 执行命令
        if args.command == 'move':
            controller.move(
                start_point=(current_pos.x, current_pos.y),
                end_point=tuple(args.to)
            )
            if hasattr(args, 'speed'):
                controller.set_speed(args.speed)
                
        elif args.command == 'click':
            if args.double:
                controller.move_and_double_click(
                    start_point=(current_pos.x, current_pos.y),
                    end_point=tuple(args.at)
                )
            elif args.button == 'right':
                controller.move_and_right_click(
                    start_point=(current_pos.x, current_pos.y),
                    end_point=tuple(args.at)
                )
            else:
                controller.move_and_click(
                    start_point=(current_pos.x, current_pos.y),
                    end_point=tuple(args.at)
                )
                
        elif args.command == 'drag':
            # 先移动到起始位置
            controller.move(
                start_point=(current_pos.x, current_pos.y),
                end_point=tuple(getattr(args, 'from'))
            )
            # 执行拖拽
            controller.drag(
                start_point=tuple(getattr(args, 'from')),
                end_point=tuple(args.to)
            )
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())