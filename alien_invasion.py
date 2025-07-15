import sys
from time import sleep

import pygame

from alien import Alien
from bullet import Bullet
from button import Button
from scoreboard import Scoreboard
from settings import Settings
from game_stats import GameStats
from ship import Ship


class AlienInvasion:
    """管理游戏资源并创建游戏资源"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        # self.screen = pygame.display.set_mode((1200, 800))
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        # self.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # 创建一个用于存储游戏统计信息的实例
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # 创建存储游戏统计信息的实例,并创建记分牌

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        # 设置背景色
        # self.bg_color=(230,230,230)
        self._create_fleet()

        # # 游戏启动后处于活动状态
        # self.game_active = True

        # 让游戏在一个开始处于非活动状态
        self.game_active = False

        # 创建Play按钮
        self.play_button = Button(self, 'Play')

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            # # 侦听键盘和鼠标事件
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         sys.exit()
            self._check_events()

            if self.game_active:

                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            # print(f"之后的子弹数：{len(self.bullets)}")
            # 每次循环时都重绘屏幕
            # self.screen.fill(self.bg_color)
            # self.screen.fill(self.settings.bg_color)
            # self.ship.blitme()
            # # 让最近绘制的屏幕可见
            # pygame.display.flip()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """响应按键和鼠标事件"""
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_event(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print("按鼠标键")
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """在玩家单击Play按钮时开始新游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # 还原游戏设置
            self.settings.initialize_dynamic_settings()

            self.game_active = True
            # 重置游戏的统计信息
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # 清空外星人列表和子弹列表
            self.bullets.empty()
            self.aliens.empty()

            # 创建一个新的外星舰队，并将飞船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()

            # 隐藏光标
            pygame.mouse.set_visible(False)

    def _check_keydown_event(self, event):
        """响应按下"""
        if event.key == pygame.K_RIGHT:
            print("玩家正在按右键")
            # 向右移动飞船
            # self.ship.rect.x+=1
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            print("玩家正在按左键")
            self.ship.moving_left = True
        elif event.key == pygame.K_ESCAPE:
            print("按下ESC键退出游戏")
            sys.exit()
        elif event.key == pygame.K_SPACE:
            print("按下空格键")
            self._fire_bullet()

    def _check_keyup_event(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """创建一颗子弹，并将其加入编组bullets"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _create_fleet(self):
        """创建一个外星舰队"""
        # 创建一个外星人，再不断添加，直到没有空间添加外星人为止
        # 外星人的间距为外星人的宽度和外星人的高度
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height-4*alien_height):

            while current_x < (self.settings.screen_width-2*alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2*alien_width
            # 添加一行外星人后，重置x值并递增y值
            current_x = alien_width
            current_y += 2*alien_height

        # self.aliens.add(alien)
    def _create_alien(self, x_position, y_position):
        """创建一个外星人并将其放在当前行中 """
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _update_aliens(self):
        """更新外星舰队中所有外星人的位置"""
        self._check_fleet_edges()
        self.aliens.update()

        # 检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            # print("Ship hit!!!")
            self._ship_hit()

        # 检查是否有外星人到达了屏幕的下边缘
        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        """在有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整个外星舰队向下移动，并改变它们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕"""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # 显示得分
        self.sb.show_score()

        # 如果游戏处于非活动状态，就绘制Play按钮
        if not self.game_active:
            self.play_button.draw_button()
        pygame.display.flip()

    def _update_bullets(self):
        """更新子弹的位置并删除已消失的子弹 """
        # 更新子弹的位置
        self.bullets.update()

        # print(f"之前的子弹数：{len(self.bullets)}")
        # 删除已消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """响应子弹和外星人的碰撞"""
        # 删除发生碰撞的子弹和外星人
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        # 检查是否有子弹击中了外星人
        # 如果是，就删除相应的子弹和外星人
        # pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points*len(aliens)
            # self.stats.score+=self.settings.alien_points
                self.sb.prep_score()
                self.sb.check_high_score()

        if not self.aliens:
            # 删除现有的子弹并创建一个新的外星舰队
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # 提高等级
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """响应飞船和外星人的碰撞"""
        if self.stats.ships_left > 0:

            # 将ships_left减1
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # 清空外星人列表和子弹列表
            self.bullets.empty()
            self.aliens.empty()

            # 创建一个新的外星舰队，并将飞船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()

            # 暂停
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕的下边缘"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # 像非常被撞到一样进行处理
                self._ship_hit()
                break


if __name__ == '__main__':
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()
