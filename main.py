# encoding:utf-8

import json
import math

import pygame

tick = 0
SCREEN = pygame.Rect(0, 0, 1200, 900)


class Mouse(pygame.sprite.Sprite):
    def __init__(self,  *group):
        super().__init__(*group)
        self.rect = pygame.Rect(0, 0, 10, 10)
        self.rect.center = pygame.mouse.get_pos()
        return

    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        return

    def collide(self, widget_group):
        collide_group = pygame.sprite.spritecollide(self, widget_group, False)
        for widget in widget_group:
            if str(type(widget)) == "<class '__main__.DynamicWidget'>":
                if widget in collide_group:
                    widget.state = "collide"
                else:
                    widget.state = "normal"
        return [widget for widget in collide_group
                if str(type(widget)) == "<class '__main__.DynamicWidget'>"]


class Background(pygame.sprite.Sprite):
    def __init__(self, image, speed, *group):
        super().__init__(*group)
        self.image = image
        self.rect = self.image.get_rect()
        screen = pygame.display.Info()
        ratio = min(screen.current_w/SCREEN.width,
                    screen.current_h/SCREEN.height)
        self.rect.center = [
            self.rect.width/2+(screen.current_w-SCREEN.width*ratio)/2,
            self.rect.height/2+(screen.current_h-SCREEN.height*ratio)/2]
        self.speed = speed
        return

    def update(self):
        screen = pygame.display.Info()
        ratio = min(screen.current_w/SCREEN.width,
                    screen.current_h/SCREEN.height)
        self.rect.centerx -= self.speed[0]
        if self.rect.centerx < SCREEN.width-self.rect.width/2 \
                + (screen.current_w-SCREEN.width*ratio)/2:
            self.rect.centerx = SCREEN.width-self.rect.width/2 \
                + (screen.current_w-SCREEN.width*ratio)/2
        self.rect.centery -= self.speed[1]
        if self.rect.centery < SCREEN.height-self.rect.height/2 \
                + (screen.current_h-SCREEN.height*ratio)/2:
            self.rect.centery = SCREEN.height-self.rect.height/2 \
                + (screen.current_h-SCREEN.height*ratio)/2
        return


class Player(pygame.sprite.Sprite):
    def __init__(self, up_image, down_image, left_image, right_image, *group):
        super().__init__(*group)
        self.up_image = up_image
        self.down_image = down_image
        self.left_image = left_image
        self.right_image = right_image
        self.image = up_image
        self.state = "down"
        self.rect = self.image.get_rect()
        self.rect.center = (400, 250)
        return

    def update(self):
        if self.state == "up":
            self.image = self.up_image
        elif self.state == "down":
            self.image = self.down_image
        elif self.state[0] == "left":
            if self.state[1] < 15:
                self.image = self.left_image[0]
            elif self.state[1] < 30:
                self.image = self.left_image[1]
            elif self.state[1] < 45:
                self.image = self.left_image[2]
            else:
                self.image = self.left_image[3]
        elif self.state[0] == "right":
            if self.state[1] < 15:
                self.image = self.right_image[0]
            elif self.state[1] < 30:
                self.image = self.right_image[1]
            elif self.state[1] < 45:
                self.image = self.right_image[2]
            else:
                self.image = self.right_image[3]
        return

    def collide(self, x, y, widget_group):
        self.rect.centerx += x
        self.rect.centery += y
        collide_group = pygame.sprite.spritecollide(self, widget_group, False)
        if [widget for widget in collide_group
                if str(type(widget)) == "<class '__main__.StativeWidget'>"]:
            self.rect.centerx -= x
            self.rect.centery -= y
        return [widget for widget in collide_group
                if str(type(widget)) == "<class '__main__.DynamicWidget'>"]


class StativeWidget(pygame.sprite.Sprite):
    def __init__(self, image, image_center, *group):
        super().__init__(*group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = image_center
        return

    def update(self):
        return


class DynamicWidget(pygame.sprite.Sprite):
    def __init__(self, base_image, extra_image, image_center, value, * group):
        super().__init__(*group)
        self.base_image = base_image
        self.extra_image = extra_image
        self.state = "normal"
        self.image = base_image
        self.rect = self.image.get_rect()
        self.rect.center = image_center
        self.value = value
        return

    def update(self):
        if self.state == "normal":
            self.image = self.base_image
        else:
            self.image = self.extra_image
        return


class Dialog:
    def __init__(self, topleft):
        self.text = []
        self.font = pygame.font.SysFont("Microsoft YaHei", 36, True, True)
        self.topleft = topleft

    def append(self, text):
        if not self.text or text != self.text[-1][1]:
            self.text.append([tick, text])
        return

    def clear(self):
        self.text = []
        return

    def render(self, main):
        global tick
        while (len(self.text) > 6 or len(self.text) > 0
                and tick-self.text[0][0] > 200):
            self.text.pop(0)
        screen = pygame.display.Info()
        ratio = min(screen.current_w/SCREEN.width,
                    screen.current_h/SCREEN.height)
        topleft = [self.topleft[0]*ratio+(screen.current_w-SCREEN.width*ratio)/2,
                   self.topleft[1]*ratio+(screen.current_h-SCREEN.height*ratio)/2]
        for text in self.text:
            main.screen.blit(self.font.render(
                text[1], True, pygame.Color("white"), pygame.Color("gray")), topleft)
            topleft[1] += 48
        return


class Widget:
    def __init__(self, file, current):
        self.tick = 0
        self.current = current
        self.group = {}
        self.background = {}
        self.player = {}
        self.stative_widget = {}
        self.dynamic_widget = {}
        with open(file, "r") as json_file:
            group = json.load(json_file)
            for group_name, widget in group.items():
                self.group[group_name] = pygame.sprite.Group()
                if "background" in widget:
                    self.background[group_name] = Background(
                        self.image_scale(widget["background"]["image"]),
                        widget["background"]["speed"],
                        self.group[group_name])
                if "player" in widget:
                    self.player[group_name] = Player(
                        self.image_scale(widget["player"]["up"]),
                        self.image_scale(widget["player"]["down"]),
                        [self.image_scale(widget["player"]["left"][0]),
                         self.image_scale(widget["player"]["left"][1]),
                         self.image_scale(widget["player"]["left"][2]),
                         self.image_scale(widget["player"]["left"][3])],
                        [self.image_scale(widget["player"]["right"][0]),
                         self.image_scale(widget["player"]["right"][1]),
                         self.image_scale(widget["player"]["right"][2]),
                         self.image_scale(widget["player"]["right"][3])],
                        self.group[group_name])
                if "stative" in widget:
                    for widget_name, attribute in widget["stative"].items():
                        self.stative_widget[widget_name] = StativeWidget(
                            self.image_scale(attribute["image"]),
                            self.center_scale(attribute["image_center"]),
                            self.group[group_name])
                if "dynamic" in widget:
                    for widget_name, attribute in widget["dynamic"].items():
                        self.dynamic_widget[widget_name] = DynamicWidget(
                            self.image_scale(attribute["base_image"]),
                            self.image_scale(attribute["extra_image"]),
                            self.center_scale(attribute["image_center"]),
                            widget_name,
                            self.group[group_name])
        return

    def render(self, main, hovered):
        if not hovered:
            main.mouse.collide(self.group[self.current])
        self.group[self.current].update()
        self.group[self.current].draw(main.screen)
        return

    def handler(self, main):
        return

    def image_scale(self, file):
        screen = pygame.display.Info()
        ratio = min(screen.current_w/SCREEN.width,
                    screen.current_h/SCREEN.height)
        image = pygame.image.load(file).convert_alpha()
        return pygame.transform.scale(
            image, (math.ceil(image.get_width()*ratio),
                    math.ceil(image.get_height()*ratio)))

    def center_scale(self, center):
        screen = pygame.display.Info()
        ratio = min(screen.current_w/SCREEN.width,
                    screen.current_h/SCREEN.height)
        return [center[0]*ratio+(screen.current_w-SCREEN.width*ratio)/2,
                center[1]*ratio+(screen.current_h-SCREEN.height*ratio)/2]


class StartupWidget(Widget):
    def handler(self, main):
        global tick
        if self.current == "epitome_1" and tick > 72:
            self.current = "epitome_2"
            return False
        elif self.current == "epitome_2" and tick > 258:
            self.current = "epitome_3"
            return False
        elif self.current == "epitome_3" and tick > 432:
            self.current = "epitome_4"
            return False
        elif self.current == "epitome_4" and tick > 546:
            self.current = "epitome_5"
            return False
        elif self.current == "epitome_5" and tick > 690:
            self.current = "epitome_6"
            return False
        elif self.current == "epitome_6" and tick > 846:
            self.current = "epitome_7"
            return False
        elif self.current == "epitome_7" and tick > 1014:
            pygame.mixer.music.load("./music/background.mp3")
            pygame.mixer.music.set_volume(0.1)
            self.current = "startup"
            return False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.current != "startup" and self.current != "continue":
                    pygame.mixer.music.load("./music/background.mp3")
                    pygame.mixer.music.set_volume(0.1)
                    self.current = "startup"
                    return False
                else:
                    for widget in main.mouse.collide(self.group[self.current]):
                        if widget.value == "exit":
                            return "exit"
                        if widget.value == "start":
                            self.current = "continue"
                            main.is_startup_widget = False
                            main.is_main_widget = True
                            main.main_widget.tick = tick
                            return False
                        if widget.value == "continue":
                            main.is_startup_widget = False
                            main.is_main_widget = True
                            main.main_widget.tick = tick
                            return False
        return False


class MainWidget(Widget):
    def __init__(self, file, current):
        self.click_tick = 0
        super().__init__(file, current)

    def handler(self, main):
        global tick
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for widget in main.mouse.collide(self.group[self.current]):
                    if widget.value == "pause":
                        main.is_pause_widget = True
                        return False
                    if widget.value == "items":
                        main.is_items_widget = True
                        return False
                    if widget.value == "sleepy_driver":
                        self.click_tick = tick
                        self.dynamic_widget["driver"].rect.center = self.center_scale([
                                                                                      1000, 800])
                        self.dynamic_widget["sleepy_driver"].rect.center = self.center_scale([
                                                                                             900, 1200])
                    if widget.value == "driver":
                        self.current = "episode_3_beaten_driver"
                        self.tick = tick
                        return False
        group = self.player[self.current].collide(
            0, 0, self.group[self.current]) if self.current in self.player else []
        if self.current in self.player:
            if pygame.key.get_pressed()[pygame.K_w]:
                self.player[self.current].state = "up"
                group += self.player[self.current].collide(
                    0, -5, self.group[self.current])
            if pygame.key.get_pressed()[pygame.K_s]:
                self.player[self.current].state = "down"
                group += self.player[self.current].collide(
                    0, +5, self.group[self.current])
            if pygame.key.get_pressed()[pygame.K_a]:
                self.player[self.current].state = ["left", tick % 60]
                group += self.player[self.current].collide(
                    -5, 0, self.group[self.current])
            if pygame.key.get_pressed()[pygame.K_d]:
                self.player[self.current].state = ["right", tick % 60]
                group += self.player[self.current].collide(
                    +5, 0, self.group[self.current])
        if self.current == "episode_1":
            main.dialog.clear()
            if tick-self.tick > 60:
                self.current = "episode_1_extra"
                self.tick = tick
            return False
        elif self.current == "episode_1_extra":
            if tick-self.tick > 60:
                self.current = "episode_1_bedchamber"
                self.player[self.current].rect.center = self.center_scale([
                    400, 700])
            return False
        elif self.current == "episode_1_bedchamber":
            for widget in group:
                if widget.value == "right":
                    self.current = "episode_1_sitting"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              200, 700])
                if widget.value == "clock":
                    main.dialog.append("你获得了一个闹钟！")
                    main.items_widget.append("clock")
                    widget.kill()
            return False
        elif self.current == "episode_1_sitting":
            for widget in group:
                if widget.value == "left":
                    self.current = "episode_1_bedchamber"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              1000, 700])
                if widget.value == "right":
                    self.current = "episode_1_kitchen"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              200, 700])
                if widget.value == "up":
                    self.current = "episode_1_gate"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              800, 700])
                if widget.value == "battery":
                    main.dialog.append("你获得了一个电池！")
                    main.items_widget.append("battery")
                    widget.kill()
            return False
        elif self.current == "episode_1_kitchen":
            for widget in group:
                if widget.value == "left":
                    self.current = "episode_1_sitting"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              1000, 700])
                if widget.value == "milk":
                    main.dialog.append("你获得了一杯牛奶！")
                    main.items_widget.append("milk")
                    widget.kill()
            return False
        elif self.current == "episode_1_gate":
            for widget in group:
                if widget.value == "up":
                    self.current = "episode_1_sitting"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              700, 600])
                if widget.value == "right":
                    self.current = "episode_1_mahjong"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              200, 700])
            return False
        elif self.current == "episode_1_mahjong":
            for widget in group:
                if widget.value == "left":
                    self.current = "episode_1_gate"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              1000, 700])
                if widget.value == "tnt":
                    main.dialog.append("你获得了一个TNT！")
                    main.items_widget.append("tnt")
                    widget.kill()
            return False
        elif self.current == "episode_1_mahjong_1":
            if tick-self.tick > 40:
                self.current = "episode_1_mahjong_2"
                tick = self.tick
            return False
        elif self.current == "episode_1_mahjong_2":
            if tick-self.tick > 30:
                self.current = "episode_1_mahjong_3"
                tick = self.tick
            return False
        elif self.current == "episode_1_mahjong_3":
            if tick-self.tick > 20:
                self.current = "episode_1_mahjong_4"
                tick = self.tick
            return False
        elif self.current == "episode_1_mahjong_4":
            if tick-self.tick > 10:
                self.current = "episode_2"
                tick = self.tick
            return False
        elif self.current == "episode_1_battery_clock":
            main.dialog.clear()
            if tick-self.tick > 100:
                return "fail"
            return False
        elif self.current == "episode_1_pour_out_milk":
            main.dialog.clear()
            if tick-self.tick > 100:
                return "fail"
            return False
        if self.current == "episode_2":
            main.dialog.clear()
            if tick-self.tick > 60:
                self.current = "episode_2_extra"
                self.tick = tick
            return False
        elif self.current == "episode_2_extra":
            if tick-self.tick > 60:
                self.current = "episode_2_bedchamber"
                self.player[self.current].rect.center = self.center_scale([
                    400, 700])
            return False
        elif self.current == "episode_2_bedchamber":
            for widget in group:
                if widget.value == "uniform_1":
                    self.current = "episode_2_bedchamber_1"
                    self.player[self.current].rect.center = \
                        self.player["episode_2_bedchamber"].rect.center
                if widget.value == "uniform_2":
                    self.current = "episode_2_bedchamber_2"
                    self.player[self.current].rect.center = \
                        self.player["episode_2_bedchamber"].rect.center
            return False
        elif self.current == "episode_2_bedchamber_1":
            for widget in group:
                if widget.value == "right":
                    self.current = "episode_2_sitting_1"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              200, 700])
                if widget.value == "uniform_1_2":
                    self.current = "episode_2_bedchamber_2"
                    self.player[self.current].rect.center = \
                        self.player["episode_2_bedchamber_1"].rect.center
            return False
        elif self.current == "episode_2_bedchamber_2":
            for widget in group:
                if widget.value == "right":
                    self.current = "episode_2_sitting_2"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              200, 700])
                if widget.value == "uniform_2_1":
                    self.current = "episode_2_bedchamber_1"
                    self.player[self.current].rect.center = \
                        self.player["episode_2_bedchamber_2"].rect.center
            return False
        elif self.current == "episode_2_sitting_1":
            for widget in group:
                if widget.value == "left":
                    self.current = "episode_2_bedchamber_1"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              1000, 700])
                if widget.value == "right":
                    self.current = "episode_2_kitchen_1"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              200, 700])
                if widget.value == "up":
                    self.current = "episode_2_gate_1"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              800, 700])
                if widget.value == "mobile_1":
                    main.dialog.append("你获得了一个手机！")
                    main.items_widget.append("mobile")
                    widget.kill()
                    self.dynamic_widget["mobile_2"].kill()

            return False
        elif self.current == "episode_2_sitting_2":
            for widget in group:
                if widget.value == "left":
                    self.current = "episode_2_bedchamber_2"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              1000, 700])
                if widget.value == "right":
                    self.current = "episode_2_kitchen_2"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              200, 700])
                if widget.value == "up":
                    self.current = "episode_2_gate_2"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              800, 700])
                if widget.value == "mobile_2":
                    main.dialog.append("你获得了一个手机！")
                    main.items_widget.append("mobile")
                    widget.kill()
                    self.dynamic_widget["mobile_1"].kill()
            return False
        elif self.current == "episode_2_kitchen_1":
            for widget in group:
                if widget.value == "left":
                    self.current = "episode_2_sitting_1"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              1000, 700])
                if widget.value == "baozi_1":
                    main.dialog.append("你获得了一袋包子！")
                    main.items_widget.append("baozi")
                    widget.kill()
                    self.dynamic_widget["baozi_2"].kill()
            return False
        elif self.current == "episode_2_kitchen_2":
            for widget in group:
                if widget.value == "left":
                    self.current = "episode_2_sitting_2"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              1000, 700])
                if widget.value == "baozi_2":
                    main.dialog.append("你获得了一袋包子！")
                    main.items_widget.append("baozi")
                    widget.kill()
                    self.dynamic_widget["baozi_1"].kill()
            return False
        elif self.current == "episode_2_gate_1":
            for widget in group:
                if widget.value == "up":
                    self.current = "episode_2_sitting_1"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              700, 600])
                if widget.value == "bus":
                    main.dialog.append("校车要穿校服才能上！")
                if widget.value == "bike":
                    if "mobile" not in main.items_widget.items:
                        main.dialog.append("没有手机怎么扫共享单车？")
                    elif not main.items_widget.eat_baozi:
                        self.current = "episode_2_eat_baozi"
                        self.tick = tick
                    else:
                        self.current = "episode_3_1"
                        tick = self.tick
            return False
        elif self.current == "episode_2_gate_2":
            for widget in group:
                if widget.value == "up":
                    self.current = "episode_2_sitting_2"
                    self.player[self.current].rect.center = self.center_scale([
                                                                              700, 600])
                if widget.value == "bus":
                    if not main.items_widget.eat_baozi:
                        self.current = "episode_2_eat_baozi"
                        self.tick = tick
                    else:
                        self.current = "episode_3_2"
                        tick = self.tick
                if widget.value == "bike":
                    main.dialog.append("穿校服还骑单车？")
            return False
        elif self.current == "episode_2_eat_baozi":
            main.dialog.clear()
            if tick-self.tick > 100:
                return "fail"
            return False
        if self.current == "episode_3_1":
            main.dialog.clear()
            if tick-self.tick > 60:
                self.current = "episode_3_extra_1"
                self.tick = tick
            return False
        elif self.current == "episode_3_extra_1":
            if tick-self.tick > 60:
                self.current = "episode_3_bike"
                self.player[self.current].rect.center = self.center_scale([
                    600, 700])
                self.tick = tick
            return False
        elif self.current == "episode_3_bike":
            if self.player[self.current].rect.centerx * 17 + \
                    self.player[self.current].rect.centery * 14 < 15600:
                self.current = "episode_3_extra_bike"
                self.tick = tick
                return False
            if self.player[self.current].rect.centerx * 6 - \
                    self.player[self.current].rect.centery * 5 > 2740:
                self.current = "episode_3_extra_bike"
                self.tick = tick
                return False
            if tick - self.tick >= 1200:
                self.current = "episode_4"
                tick = self.tick
            elif (1200 - tick + self.tick) % 60 == 0:
                main.dialog.append(
                    "还剩"+str((1200 - tick + self.tick)//60)+"秒到学校！")
            elif tick - self.tick == 100:
                self.dynamic_widget["shadow"].rect.center = self.center_scale([
                    600, 700])
            elif tick - self.tick == 250:
                self.dynamic_widget["shadow"].rect.center = self.center_scale([
                                                                              900, 1200])
                for widget in group:
                    if widget.value == "shadow":
                        self.current = "episode_3_crash_bike"
                        self.tick = tick
                        return False
            elif tick - self.tick == 400:
                self.dynamic_widget["shadow"].rect.center = self.center_scale([
                    400, 600])
            elif tick - self.tick == 550:
                self.dynamic_widget["shadow"].rect.center = self.center_scale([
                                                                              900, 1200])
                for widget in group:
                    if widget.value == "shadow":
                        self.current = "episode_3_crash_bike"
                        self.tick = tick
                        return False
            elif tick - self.tick == 700:
                self.dynamic_widget["shadow"].rect.center = self.center_scale([
                    700, 600])
            elif tick - self.tick == 850:
                self.dynamic_widget["shadow"].rect.center = self.center_scale([
                                                                              900, 1200])
                for widget in group:
                    if widget.value == "shadow":
                        self.current = "episode_3_crash_bike"
                        self.tick = tick
                        return False
            elif tick - self.tick == 1000:
                self.dynamic_widget["shadow"].rect.center = self.center_scale([
                    600, 500])
            elif tick - self.tick == 1150:
                self.dynamic_widget["shadow"].rect.center = self.center_scale([
                                                                              900, 1200])
                for widget in group:
                    if widget.value == "shadow":
                        self.current = "episode_3_crash_bike"
                        self.tick = tick
                        return False
            return False
        elif self.current == "episode_3_crash_bike":
            main.dialog.clear()
            if tick-self.tick > 100:
                return "fail"
            return False
        elif self.current == "episode_3_extra_bike":
            main.dialog.clear()
            if tick-self.tick > 100:
                return "fail"
            return False
        if self.current == "episode_3_2":
            main.dialog.clear()
            if tick-self.tick > 60:
                self.current = "episode_3_extra_2"
                self.tick = tick
            return False
        elif self.current == "episode_3_extra_2":
            if tick-self.tick > 60:
                self.current = "episode_3_bus"
                self.player[self.current].rect.center = self.center_scale([
                    200, 750])
                self.tick = tick
            return False
        elif self.current == "episode_3_bus":
            if tick - self.tick >= 1200:
                self.current = "episode_4"
                tick = self.tick
            elif (1200 - tick + self.tick) % 60 == 0:
                main.dialog.append(
                    "还剩"+str((1200 - tick + self.tick)//60)+"秒到学校！")
            elif tick - self.tick == 100:
                self.dynamic_widget["driver"].rect.center = self.center_scale([
                                                                              900, 1200])
                self.dynamic_widget["sleepy_driver"].rect.center = self.center_scale([
                                                                                     1000, 800])
                self.click_tick = 0
            elif tick - self.tick == 250 and not self.click_tick:
                self.current = "episode_3_sleepy_driver"
                self.tick = tick
                return False
            elif tick - self.tick == 400:
                self.dynamic_widget["driver"].rect.center = self.center_scale([
                                                                              900, 1200])
                self.dynamic_widget["sleepy_driver"].rect.center = self.center_scale([
                                                                                     1000, 800])
                self.click_tick = 0
            elif tick - self.tick == 550 and not self.click_tick:
                self.current = "episode_3_sleepy_driver"
                self.tick = tick
                return False
            elif tick - self.tick == 700:
                self.dynamic_widget["driver"].rect.center = self.center_scale([
                                                                              900, 1200])
                self.dynamic_widget["sleepy_driver"].rect.center = self.center_scale([
                                                                                     1000, 800])
                self.click_tick = 0
            elif tick - self.tick == 850 and not self.click_tick:
                self.current = "episode_3_sleepy_driver"
                self.tick = tick
                return False
            elif tick - self.tick == 1000:
                self.dynamic_widget["driver"].rect.center = self.center_scale([
                                                                              900, 1200])
                self.dynamic_widget["sleepy_driver"].rect.center = self.center_scale([
                                                                                     1000, 800])
                self.click_tick = 0
            elif tick - self.tick == 1150 and not self.click_tick:
                self.current = "episode_3_sleepy_driver"
                self.tick = tick
                return False
        elif self.current == "episode_3_sleepy_driver":
            main.dialog.clear()
            if tick-self.tick > 100:
                return "fail"
            return False
        elif self.current == "episode_3_beaten_driver":
            main.dialog.clear()
            if tick-self.tick > 100:
                return "fail"
            return False
        if self.current == "episode_4":
            main.dialog.clear()
            pygame.mixer.music.stop()
            if tick-self.tick > 60:
                self.current = "episode_4_extra"
                self.tick = tick
            return False
        elif self.current == "episode_4_extra":
            pygame.mixer.music.stop()
            if tick-self.tick > 60:
                pygame.mixer.music.load("./music/epilogue.mp3")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play()
                self.current = "episode_4_1"
                self.tick = tick
            return False
        elif self.current == "episode_4_1":
            if tick-self.tick > 180:
                self.current = "episode_4_2"
                self.tick = tick
            return False
        elif self.current == "episode_4_2":
            if tick-self.tick > 180:
                self.current = "episode_4_3"
                self.tick = tick
            return False
        elif self.current == "episode_4_3":
            if tick-self.tick > 180:
                self.current = "episode_4_4"
                self.tick = tick
            return False
        elif self.current == "episode_4_4":
            if tick-self.tick > 180:
                self.current = "episode_4_5"
                self.tick = tick
            return False
        elif self.current == "episode_4_5":
            if tick-self.tick > 372:
                self.current = "episode_4_6"
                self.tick = tick
            return False
        elif self.current == "episode_4_6":
            if tick-self.tick > 180:
                self.current = "episode_4_7"
                self.tick = tick
            return False
        elif self.current == "episode_4_7":
            if tick-self.tick > 60:
                self.current = "episode_4_8"
                self.tick = tick
            return False
        elif self.current == "episode_4_8":
            if tick-self.tick > 60:
                self.current = "episode_4_9"
                self.tick = tick
            return False
        elif self.current == "episode_4_9":
            if tick-self.tick > 60:
                self.current = "episode_4_10"
                self.tick = tick
            return False
        elif self.current == "episode_4_10":
            if tick-self.tick > 60:
                self.current = "episode_4_11"
                self.tick = tick
            return False
        elif self.current == "episode_4_11":
            if tick-self.tick > 60:
                self.current = "episode_4_12"
                self.tick = tick
            return False
        elif self.current == "episode_4_12":
            if tick-self.tick > 60:
                self.current = "episode_4_13"
                self.tick = tick
            return False
        elif self.current == "episode_4_13":
            if tick-self.tick > 120:
                self.current = "episode_4_14"
                self.tick = tick
            return False
        elif self.current == "episode_4_14":
            if tick-self.tick > 60:
                self.current = "episode_4_15"
                self.tick = tick
            return False
        elif self.current == "episode_4_15":
            if tick-self.tick > 60:
                self.current = "epilogue"
                self.tick = tick
            return False
        if self.current == "epilogue":
            main.dialog.clear()
            pygame.mixer.music.stop()
            if tick-self.tick > 60:
                pygame.mixer.music.load("./music/complete.mp3")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play()
                self.current = "epilogue_1"
                self.tick = tick
                return False
            return False
        if self.current == "epilogue_1":
            if tick-self.tick > 200:
                self.current = "epilogue_2"
                self.tick = tick
                return False
            return False
        if self.current == "epilogue_2":
            if tick-self.tick > 200:
                self.current = "epilogue_3"
                self.tick = tick
                return False
            return False
        if self.current == "epilogue_3":
            if tick-self.tick > 200:
                self.current = "epilogue_4"
                self.tick = tick
                return False
            return False
        if self.current == "epilogue_4":
            if tick-self.tick > 200:
                self.current = "epilogue_5"
                self.tick = tick
                return False
            return False
        if self.current == "epilogue_5":
            if tick-self.tick > 200:
                self.current = "epilogue_6"
                self.tick = tick
                return False
            return False
        if self.current == "epilogue_6":
            if tick-self.tick > 200:
                return "complete"
        return False


class PauseWidget(Widget):
    def handler(self, main):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for widget in main.mouse.collide(self.group[self.current]):
                    if widget.value == "continue":
                        main.is_pause_widget = False
                        return False
                    if widget.value == "pause":
                        main.is_pause_widget = False
                        main.is_main_widget = False
                        main.is_startup_widget = True
                        return False
        return False


class ItemsWidget(Widget):
    def __init__(self, file, current):
        self.items = []
        self.battery_clock = False
        self.pour_out_milk = False
        self.eat_baozi = False
        super().__init__(file, current)

    def render(self, main, hovered):
        center = [1150, 250]
        self.items = list(set(self.items))
        for widget in self.dynamic_widget:
            if widget in self.items:
                self.dynamic_widget[widget].rect.center = self.center_scale(
                    center)
                center[1] += 100
            elif widget != "items":
                self.dynamic_widget[widget].rect.center = self.center_scale([
                                                                            1250, 950])
        super().render(main, hovered)
        return

    def handler(self, main):
        global tick
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for widget in main.mouse.collide(self.group[self.current]):
                    if widget.value == "items":
                        main.is_items_widget = False
                        return False
                    if widget.value == "clock":
                        if (self.battery_clock and
                                main.main_widget.current == "episode_1_bedchamber"):
                            widget.kill()
                            self.items.remove("clock")
                            main.main_widget.stative_widget["clock"] = StativeWidget(
                                self.image_scale(
                                    "./image/bedchamber/clock.png"),
                                self.center_scale([150, 575]),
                                main.main_widget.group["episode_1_bedchamber"])
                            main.dialog.append("有电的闹钟，好棒！")
                        elif self.battery_clock:
                            main.dialog.append("闹钟怎么能放在卧室外呢？")
                        else:
                            main.dialog.append("没电的闹钟要它有什么用？")
                        return False
                    if widget.value == "battery":
                        if "clock" in self.items:
                            widget.kill()
                            self.items.remove("battery")
                            self.battery_clock = True
                            main.dialog.append("闹钟装上了电池。")
                        else:
                            main.dialog.append("没有闹钟，电池装在哪里呢？")
                        return False
                    if widget.value == "milk":
                        if main.main_widget.current == "episode_1_gate":
                            widget.kill()
                            self.items.remove("milk")
                            self.pour_out_milk = True
                            main.dialog.append("牛奶被倒掉了，好可惜（")
                        else:
                            widget.kill()
                            self.items.remove("milk")
                            main.dialog.append("牛奶被喝掉了，味道很好）")
                    if widget.value == "tnt":
                        if main.main_widget.current == "episode_1_mahjong":
                            widget.kill()
                            self.items.remove("tnt")
                            main.is_items_widget = False
                            if not self.battery_clock:
                                main.main_widget.current = "episode_1_battery_clock"
                                main.main_widget.tick = tick
                            elif not self.pour_out_milk:
                                main.main_widget.current = "episode_1_pour_out_milk"
                                main.main_widget.tick = tick
                            else:
                                main.main_widget.current = "episode_1_mahjong_1"
                                main.main_widget.tick = tick
                        else:
                            main.dialog.append("拆家是不好的，快去炸麻将馆！")
                        return False
                    if widget.value == "mobile":
                        main.dialog.append("手机有什么用呢？")
                    if widget.value == "baozi":
                        widget.kill()
                        self.items.remove("baozi")
                        self.eat_baozi = True
                        main.dialog.append("包子真香！")

        return False

    def append(self, name):
        self.items.append(name)
        return


class Main:
    def __init__(self):
        screen = pygame.display.Info()
        self.screen = pygame.display.set_mode(
            (screen.current_w, screen.current_h), pygame.FULLSCREEN)
        self.startup_widget = StartupWidget(
            "./startup_widget.json", "epitome_1")
        self.main_widget = MainWidget("./main_widget.json", "episode_1")
        self.items_widget = ItemsWidget("./items_widget.json", "items")
        self.pause_widget = PauseWidget("./pause_widget.json", "pause")
        self.is_startup_widget = False
        self.is_main_widget = False
        self.is_items_widget = False
        self.is_pause_widget = False
        self.dialog = Dialog([0, 0])
        self.mouse = Mouse()
        return

    def render(self):
        if self.is_startup_widget:
            self.startup_widget.render(self, False)
        if self.is_main_widget:
            self.main_widget.render(
                self, self.is_pause_widget)
            if self.is_pause_widget:
                self.pause_widget.render(self, False)
            if self.is_items_widget:
                self.items_widget.render(self, False)
        return

    def handler(self):
        if self.is_startup_widget:
            return self.startup_widget.handler(self)
        if self.is_main_widget:
            if self.is_pause_widget:
                return self.pause_widget.handler(self)
            if self.is_items_widget:
                return self.items_widget.handler(self)
            return self.main_widget.handler(self)

    def exec(self):
        clock = pygame.time.Clock()
        screen = pygame.display.Info()
        ratio = min(screen.current_w/SCREEN.width,
                    screen.current_h/SCREEN.height)
        global tick
        self.is_startup_widget = True
        pygame.mixer.music.load("./music/epitome.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()
        complete = False
        while True:
            self.mouse.update()
            self.render()
            self.dialog.render(self)
            res = self.handler()
            if res == "exit":
                break
            if res == "complete":
                complete = True
            if res == "complete" or res == "fail":
                self.startup_widget = StartupWidget(
                    "./startup_widget.json", "startup")
                self.main_widget = MainWidget(
                    "./main_widget.json", "episode_1")
                self.items_widget = ItemsWidget("./items_widget.json", "items")
                self.pause_widget = PauseWidget("./pause_widget.json", "pause")
                self.is_startup_widget = True
                self.is_main_widget = False
                self.is_items_widget = False
                self.is_pause_widget = False
                if complete:
                    self.startup_widget.stative_widget["title_glowing_1"].rect.center = \
                        self.startup_widget.center_scale([600, 300])
                    self.startup_widget.stative_widget["title_glowing_2"].rect.center = \
                        self.startup_widget.center_scale([600, 300])
                    self.pause_widget.stative_widget["title_glowing"].rect.center = \
                        self.startup_widget.center_scale([600, 300])
                    self.items_widget.stative_widget["extra_1"].rect.center = \
                        self.startup_widget.center_scale([600, 775])
                    self.items_widget.stative_widget["extra_2"].rect.center = \
                        self.startup_widget.center_scale([500, 775])
                    self.items_widget.stative_widget["extra_3"].rect.center = \
                        self.startup_widget.center_scale([400, 800])
                    self.items_widget.stative_widget["extra_4"].rect.center = \
                        self.startup_widget.center_scale([300, 800])
                    self.items_widget.stative_widget["extra_5"].rect.center = \
                        self.startup_widget.center_scale([200, 800])
            pygame.draw.rect(self.screen, pygame.Color("black"), pygame.Rect(
                0, 0, (screen.current_w-SCREEN.width*ratio)/2, screen.current_h))
            pygame.draw.rect(self.screen, pygame.Color("black"), pygame.Rect(
                0, 0, screen.current_w, (screen.current_h-SCREEN.height*ratio)/2))
            pygame.draw.rect(self.screen, pygame.Color("black"), pygame.Rect(
                (screen.current_w+SCREEN.width*ratio)/2, 0,
                (screen.current_w-SCREEN.width*ratio)/2, screen.current_h))
            pygame.draw.rect(self.screen, pygame.Color("black"), pygame.Rect(
                0, (screen.current_h+SCREEN.height*ratio)/2,
                screen.current_w, (screen.current_h-SCREEN.height*ratio)/2))
            pygame.display.update()
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
            tick += 1
            clock.tick(60)
        pygame.mixer.music.stop()
        return


pygame.init()
pygame.mixer.init()
Main().exec()
pygame.mixer.quit()
pygame.quit()
