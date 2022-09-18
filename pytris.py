#pylint:disable=W0611
import pygame
from random import choice,randint

pygame.init()

class Config():
    def __init__(self):
        self.debug = False
        self.debug_total_tetris = False
        self.rotation_kick = False
        self.screen_w = 300
        self.screen_h = 400
        self.bg = (210,210,210)
        self.border_bg = (180,180,180)
        self.grid_pos = (20,20)
        
        self.grid_w = 10
        self.grid_h = 20

        self.cell_size = 15
        self.cell_gap = 2
        self.inactive_cell_bg = (170,200,180)
        
        self.grid_bg = (180,210,190)
        
        self.spawn_point = (self.grid_w//2)-2
        
        self.black_cell = False
        self.black_cell_color = (60,70,90)
        self.cell_colors={1:(255,94,14),2:(0,0,170),3:(255,20,10),4:(20,150,30),5:(0,130,130),6:(155,38,182),7:(230,230,0)}
        self.next_block_pos = self.grid_w*(self.cell_size+self.cell_gap)+(self.cell_size*2),70
        self.key_pressed_hold = True
        self.base_speed = 0.5
        self.speed_incr = 0.05
        self.level_up_score = 5000
        self.starting_level = 5
        
        self.score_pos = self.next_block_pos[0],self.next_block_pos[1]+(self.cell_size+self.cell_gap)*4
        self.level_pos = self.score_pos[0],self.score_pos[1]+50
    def set_screen(self,w,h):
        self.screen_w=w
        self.screen_h=h
        self.cell_size = int(0.05*w)
        self.grid_pos=(int(0.067*w),)*2
        self.next_block_pos = self.grid_w*(self.cell_size+self.cell_gap)+(self.cell_size*2),0.14*self.screen_w
        self.score_pos = self.next_block_pos[0],self.next_block_pos[1]+(self.cell_size+self.cell_gap)*4
        self.level_pos = self.score_pos[0],self.score_pos[1]+50
    def random_color(self):
        for i in range(1,8,1):
            self.cell_colors[i]=[randint(0,255) for _ in range(3)]
    def get_cell_color(self,cell):
        if self.black_cell:
            return self.black_cell_color
        else:
            if cell in self.cell_colors:
                return self.cell_colors[cell]
            return self.black_cell_color
conf= Config()

class Block():
    def __init__(self):
        self.grid_size = None
        self.grid = None
        self.repr = None
        
    def calc_grid_size(self,l):
        max_x = 0
        max_y = 0
        for x,y in l:
            max_x = max(max_x,x)
            max_y = max(max_y,y)
        grid_size = max(max_x,max_y)+1
        return grid_size
        
    def list_to_grid(self,l,grid_size):
        temp_grid = [[0]*grid_size for _ in range(grid_size)]
        for x,y in l:
            temp_grid[y][x]=self.repr
        return temp_grid
    @classmethod
    def from_classic(cls,name=None):
        temp_cls = cls()
        names = ["L","J","Z","S","I","T","O"]
        if not name:
            if conf.debug_total_tetris:
                name = "I"
            else:
                name = choice(names)
        else:
            name = name.upper()
        
        temp_block = None
                                              #
        if name=="L":       #orange ricky   ###
            temp_block=[(0,1),(1,1),(2,1),(2,0)]
                                            #
        elif name=="J":     #blue ricky     ###
            temp_block=[(0,0),(0,1),(1,1),(2,1)]
                                            ##
        elif name=="Z":     #cleveland z     ##
            temp_block=[(0,0),(1,0),(1,1),(2,1)]
                                              ##
        elif name=="S":     #rhode island z  ##
            temp_block=[(1,0),(2,0),(0,1),(1,1)]
        
        elif name=="I":     #hero           ####
            temp_block=[(0,1),(1,1),(2,1),(3,1)]
                                             #
        elif name=="T":     #teewee         ###
            temp_block=[(1,0),(0,1),(1,1),(2,1)]
                                            ##
        elif name =="O":    #smashboy       ##
            temp_block=[(0,0),(1,0),(0,1),(1,1)]
            
        temp_cls.repr = names.index(name)+1
        temp_cls.grid_size = temp_cls.calc_grid_size(temp_block)
        temp_cls.grid = temp_cls.list_to_grid(temp_block,temp_cls.grid_size)
        
        return temp_cls
        
    def rotate(self,clockwise=0):
        new_grid = [[0]*self.grid_size for _ in range(self.grid_size)]
        for a in range(self.grid_size):
            for b in range(self.grid_size):
                value = self.grid[a][b]
                if clockwise: #rotate clockwise
                    move = self.grid_size-1-a
                    new_grid[b][move] = value
                else:
                    move = self.grid_size-1-b
                    new_grid[move][a] = value
        block = Block()
        block.grid_size = self.grid_size
        block.repr= self.repr
        block.grid = new_grid
        return block
        
    def __iter__(self):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                yield (x,y,self[x,y])
                
    def __str__(self):
        string = ""
        for row in self.grid:
            for element in row:
                if element:
                    string+="# "
                else:
                    string+=". "
            string+="\n"
        return string
        
    def __getitem__(self,xy):
        x,y = xy
        return self.grid[y][x]

class Tetris_Collision():
    def __init__(self,type_,boolean):
        self.type = type_
        self.bool = boolean
    def __bool__(self):
        return self.bool

class TetrisEngine():
    def __init__(self,x,y):
        self.w = x
        self.h = y
        
        self.grid = [[0]*x for _ in range(y)]
        
        self.block = Block.from_classic()
        self.next_block = Block.from_classic()
        self.block_pos = conf.spawn_point,-3
        
        self.debug_cells = []
        
        self.last_move = None
        
        self.space_available = True
        self.non_zero_row = []
        self.placed_score = False
        
        self.need_to_clean_row = self.h-1
        
    def debug_brick(self,x,y,value=100):
        if conf.debug:
            self[x,y] = value
            
    def row_check(self):
        self.non_zero_row = []
        _,ybegin = self.block_pos
        yend = self.block.grid_size
        for y in range(ybegin,ybegin+yend+1,1):
            if y<self.h:
                if not 0 in self.grid[y]:
                    self.non_zero_row.append(y)
                
    def collision(self,block_obj,x,y):
        for bx,by,bval in block_obj:
            if bval:
                #order of if is important
                if not 0<=bx+x<self.w:
                    return Tetris_Collision("wall",True) #collided with side wall
                elif by+y>=self.h:
                    return Tetris_Collision("floor",True) #collided with brick
                elif by+y>=0:
                    if self[bx+x,by+y]:
                        return Tetris_Collision("brick",True) #collided with brick
                
        return False
        
    def collision_handler(self,collision):
        if conf.debug:
            print(collision.type)
        if self.last_move == "d":
            if collision.type =="brick" or collision.type=="floor":
                _,by = self.block_pos
                if by<0:
                    self.space_available=False
                else:
                    self.fixed_block()
                    self.row_check()
                    self.block = self.next_block
                    self.next_block = Block.from_classic()
                    self.block_pos = conf.spawn_point,-3
                    
    def place_block(self):
        pos_x, pos_y = self.block_pos
        for x,y,val in self.block:
            if val and pos_y+y>=0:
                self.grid[pos_y+y][pos_x+x] = val
            else:
                if conf.debug:
                    self.debug_cells.append((pos_x+x,pos_y+y))
    def rotate_kick(self,rotated_block):
        pass
    def rotate(self,clockwise=1):
        self.clear_block()
        rotated_block= self.block.rotate(clockwise)
        if not self.collision(rotated_block,*self.block_pos):
            self.block = rotated_block
        else:
            if conf.rotation_kick:
                pass
        self.place_block()
        
    def move(self,direction="r"):
        position = self.block_pos
        pos_x, pos_y = position
        self.clear_block()
        if direction=="r": #right
            position = pos_x+1, pos_y
        elif direction=="l": #left
            position = pos_x-1, pos_y
        elif direction == "d": #down
            position = pos_x, pos_y+1
        elif direction == "u": #up only for debug
            position = pos_x, pos_y-1
        
        self.last_move = direction
        
        if not (collision:=self.collision(self.block, *position)):
            self.block_pos = position
        else:
            self.collision_handler(collision)
        
        self.place_block()
            
    def clear_block(self):
        pos_x, pos_y = self.block_pos
        for x,y,val in self.block:
            if val and pos_y+y>=0:
                self.grid[pos_y+y][pos_x+x] = 0
        if conf.debug:
            self.debug_cells=[]
            
    def fixed_block(self):
        pos_x, pos_y = self.block_pos
        for x,y,val in self.block:
            if val and pos_y+y>=0:
                self.grid[pos_y+y][pos_x+x] = val
        self.placed_score = True
    def game_over_cleanup(self):
        if 0<=self.need_to_clean_row<self.h:
            self.grid.pop(self.need_to_clean_row)
            self.grid.insert(self.need_to_clean_row,[0]*self.w)
            self.need_to_clean_row -=1

    def __str__(self):
        string = ""
        for row in self.grid:
            for element in row:
                if element:
                    string+="# "
                else:
                    string+=". "
            string+="\n"
        return string
    def __getitem__(self,xy):
        x,y = xy
        return self.grid[y][x]
    def __setitem__(self,xy,value):
        x,y = xy
        self.grid[y][x] = value
    def __iter__(self):
        for y in range(self.h):
            for x in range(self.w):
                yield (x,y,self[x,y])

        
class Game():
    def __init__(self,pygame_screen):
        self.screen = pygame_screen
        self.tetris = TetrisEngine(10,20)
        self.tetris.place_block()
        self.cell_dim = conf.cell_size+conf.cell_gap
        self.grid_x, self.grid_y = conf.grid_pos
        self.nblock_x,self.nblock_y = conf.next_block_pos
        rect_x =self.grid_x - self.grid_x/3
        rect_y = self.grid_y - self.grid_y/3
        self.grid_bg_rect = rect_x,rect_y,conf.screen_w - (rect_x*2), conf.grid_h * self.cell_dim + rect_y
        self.font = pygame.font.SysFont("monospace",30)
        self.level = conf.starting_level
        self.score =0
        
        self.game_stop = False
        self.game_clock = pygame.time.Clock()
        self.time_passed = 0
        
        self.game_speed = conf.base_speed - (conf.speed_incr*self.level)
        self.clock = None
        self.non_zero_remove_time = 0
        self.total_tetris = False
        self.score_srf = self.font.render(f"{self.score}",2,(0,0,0))
        self.level_srf = self.font.render(f"L {self.level}",2,(0,0,0))
        
        self.game_over_srf = self.font.render("Game Over",2,(0,0,0))
        over_x,over_y = self.game_over_srf.get_size()
        self.game_over_pos = conf.grid_pos[0]+conf.grid_w*(conf.cell_size+conf.cell_gap)/2 - over_x/2,conf.grid_h*(conf.cell_size+conf.cell_gap)/2 - over_y/2 + conf.grid_pos[1]
        
        self.start_srf = self.font.render("press down to start",2,(0,0,0))
        over_x,over_y = self.game_over_srf.get_size()
        self.start_pos = conf.grid_pos[0]+conf.grid_w*(conf.cell_size+conf.cell_gap)/2 - over_x/2,conf.grid_h*(conf.cell_size+conf.cell_gap)/2 - over_y/2 + conf.grid_pos[1]
        
    def rand_color(self,begin=0,end=255):
        if conf.black_cell:
            return [randint(begin,end)]*3
        return [randint(begin,end) for _ in range(3)]
        
    def draw_cell(self,x,y,cell,pos_x,pos_y,draw_inactive=1,non_zero=False):
        points = pos_x+(self.cell_dim)*x,pos_y+(self.cell_dim)*y,conf.cell_size,conf.cell_size
        if 0<cell<100:
            color = conf.get_cell_color(cell)
            if non_zero:
                pygame.draw.rect(self.screen,self.rand_color(begin=180),points)
            else:
                pygame.draw.rect(self.screen,color,points)
            if conf.black_cell:
                pygame.draw.rect(self.screen,(20,20,20),points,width=1)
            else:
                pygame.draw.rect(self.screen,(30,40,30),points,width=1)
        elif cell==100: #debug cell
            pygame.draw.rect(self.screen,(255,0,0),points)
        else:
            if draw_inactive:
                pygame.draw.rect(self.screen,conf.inactive_cell_bg,points)
            if conf.debug:
                if (x,y) in self.tetris.debug_cells:
                    pygame.draw.rect(self.screen,(0,0,255),points)
                    
    def non_zero_row(self):
        nzr = self.tetris.non_zero_row
        if nzr:
            if not self.clock:
                self.clock=pygame.time.Clock()
                self.total_tetris = True if len(nzr)==4 else False
            self.non_zero_remove_time+= self.clock.tick()/1000
            if self.non_zero_remove_time>0.5:
                self.tetris.clear_block()
                for i,y in enumerate(nzr):
                    self.score+= (50*(self.level+1)*(i+1))
                    self.tetris.grid.pop(y)
                    self.tetris.grid.insert(0,[0]*self.tetris.w)
                self.tetris.place_block()
                self.tetris.non_zero_row=[]
                self.clock=0
                self.non_zero_remove_time=0
                self.total_tetris= False
                self.score_srf = self.font.render(f"{self.score}",2,(0,0,0))
        
    def render(self):
        if self.total_tetris:
            pygame.draw.rect(self.screen, self.rand_color(230,255), self.grid_bg_rect)
        else:
            pygame.draw.rect(self.screen, conf.grid_bg, self.grid_bg_rect)
        pygame.draw.rect(self.screen, conf.border_bg, self.grid_bg_rect,width=2)
        for x,y,cell in self.tetris:
            if y in self.tetris.non_zero_row:
                self.draw_cell(x,y,cell,self.grid_x,self.grid_y,non_zero=True)
            else:
                self.draw_cell(x,y,cell,self.grid_x,self.grid_y)
        for x,y,cell in self.tetris.next_block:
            self.draw_cell(x,y,cell,self.nblock_x,self.nblock_y,0)
        self.screen.blit(self.score_srf,conf.score_pos)
        self.screen.blit(self.level_srf,conf.level_pos)
        if not self.tetris.space_available and self.tetris.need_to_clean_row>-1:
            self.screen.blit(self.game_over_srf,self.game_over_pos)
        elif not self.tetris.space_available:
            self.screen.blit(self.start_srf,self.start_pos)
    
    def restart(self):
        self.level = conf.starting_level
        self.score =0
        self.game_speed = conf.base_speed - (conf.speed_incr*self.level)
        self.clock = None
        self.non_zero_remove_time = 0
        self.total_tetris = False
        self.score_srf = self.font.render(f"{self.score}",2,(0,0,0))
        self.level_srf = self.font.render(f"L {self.level}",2,(0,0,0))        
        self.tetris.need_to_clean_row = conf.grid_h-1
        self.tetris.space_available=True
        self.game_stop = False
        
    def score_and_level(self):
        if self.score>(conf.level_up_score*(abs(conf.starting_level-self.level)+1)):
            self.level +=1
            self.level_srf = self.font.render(f"L {self.level}",2,(0,0,0))
            self.game_speed=conf.base_speed - (conf.speed_incr*self.level)

    def cycle(self):
        if self.tetris.space_available:
            self.time_passed+= self.game_clock.tick()/1000
            if self.time_passed>self.game_speed:
                if self.tetris.placed_score:
                    self.score += (5*(self.level+1))
                    self.score_srf = self.font.render(f"{self.score}",2,(0,0,0))
                    self.tetris.placed_score = False
                self.tetris.move("d")
                self.time_passed = 0
                self.score_and_level()
            self.non_zero_row()
        elif self.tetris.need_to_clean_row!=-1:
            self.time_passed+= self.game_clock.tick()/1000
            if self.time_passed>self.game_speed:
                self.tetris.game_over_cleanup()
                self.time_passed = 0
        else:
            self.game_stop = True
        self.render()
def play():
    screen = pygame.display.set_mode((conf.screen_w,conf.screen_h))
    game = Game(screen)
    move_mode_pressed = None
    clock=pygame.time.Clock()
    pressed_time = 0
    while True:
        screen.fill(conf.bg)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYUP:
                move_mode_pressed=None
            if event.type == pygame.KEYDOWN:
                if event.key == 1073741903:   #right
                    move_mode_pressed='r'
                elif event.key == 1073741904: #left
                    move_mode_pressed='l'
                elif event.key == 1073741905: #down
                    if game.game_stop:
                        game.restart()
                    move_mode_pressed='d'
                elif event.key == 1073741906: #up
                    if conf.debug:
                        game.tetris.move('u')
                    else:
                        game.tetris.rotate(1)#clockwise
                    
                elif event.key == 97: #a
                    game.tetris.rotate(0)#counter clockwise
                elif event.key == 115: #s
                    game.tetris.rotate(0)#clockwise
                elif event.unicode == 'c':
                    conf.black_cell = not conf.black_cell

        if conf.key_pressed_hold:
            if move_mode_pressed:
                pressed_time += clock.tick()/1000
                if move_mode_pressed=="d":
                    if pressed_time>0.05:
                        game.tetris.move(move_mode_pressed)
                        pressed_time = 0
                else:
                    if pressed_time>0.1:
                        game.tetris.move(move_mode_pressed)
                        pressed_time = 0
        else:
            game.tetris.move(move_mode_pressed)
            move_mode_pressed = None
        game.cycle()
        pygame.display.flip()
if __name__=="__main__":
    if (in_android:=not True):
        conf.set_screen(720,1440)
        #conf.random_color()
    else:
        conf.set_screen(500,630)
    conf.black_cell=False
    conf.starting_level=5
    conf.level_up_score = 5000
    play()
