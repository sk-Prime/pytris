import pygame, math
from random import choice,randint

pygame.init()

class Config():
    def __init__(self):
        self.debug = False
        self.debug_placement = False
        self.debug_block_type = False
        self.debug_block_name = 'L'
        self.debug_stop_falling = False
        self.debug_tetris_grid = False
        self.debug_score_and_level = False
        self.ascii_repr_char = '#'
        
        self.rotation_kick = False
        self.screen_w = 300
        self.screen_h = 400
        
        #Tetris main grid dimensions. default is classic 10 by 20
        self.grid_w = 10
        self.grid_h = 20
        #grid position (top left corner) on window
        self.grid_display_pos = (20,20)
        
        self.bg = (210,210,210)
        self.border_bg = (180,180,180)
        
        #grid cell size and gap between cell. used in pygame.draw.rect
        self.cell_size = 15
        self.cell_gap = 2
        
        #all colors
        self.grid_bg = (180,210,190)
        self.cell_colors={1:(255,94,14),2:(0,0,170),3:(255,20,10),4:(20,150,30),5:(0,130,130),6:(155,38,182),7:(230,230,0)}
        self.inactive_cell_color = (170,200,180)
        self.black_cell = False #draw black cell
        self.black_cell_color = (60,70,90)
        self.draw_cell_border = True
        
        #block spawn at this position of main grid
        self.spawn_point = (self.grid_w//2)-2
        
        #it will be multiplied by level and number of rows removed at a time
        self.score_base = 50
        
        self.base_speed = 5
        
        self.level_up_by_score = not True
        self.starting_level = 0
        self.level_up_score = 10000
        self.level_up_line = 10
        
        #grid width in pixel
        self.grid_pw = self.grid_w*(self.cell_size+self.cell_gap)
        self.grid_ph = self.grid_h*(self.cell_size+self.cell_gap)
        
        #the coming block will bo shown in this position on window
        self.next_block_display_pos = self.grid_pw+(self.cell_size*2),70
        self.score_display_pos = self.next_block_display_pos[0],self.next_block_display_pos[1]+(self.cell_size+self.cell_gap)*4
        self.level_display_pos = self.score_display_pos[0],self.score_display_pos[1]+50
        self.line_display_pos = self.score_display_pos[0],self.level_display_pos[1]+50
        
        self.key_pressed_hold = True
        self.boom_duration = 0.4 #tetris row removing animation duration
        
        
    def set_screen(self,w,h):
        self.screen_w=w
        self.screen_h=h
        self.cell_size = ((w-(w*50/100) + (conf.grid_w*conf.cell_gap)) // (conf.grid_w))  #int(0.05*w)
        self.grid_display_pos=(int(0.067*w),)*2
        
        self.grid_pw = self.grid_w*(self.cell_size+self.cell_gap)
        self.grid_ph = self.grid_h*(self.cell_size+self.cell_gap)
        self.next_block_display_pos = self.grid_display_pos[0] + self.grid_w*(self.cell_size+self.cell_gap)+5,self.grid_display_pos[1]+10
        self.score_display_pos = self.next_block_display_pos[0],self.next_block_display_pos[1]+(self.cell_size+self.cell_gap)*4
        self.level_display_pos = self.score_display_pos[0],self.score_display_pos[1]+50
        self.line_display_pos = self.score_display_pos[0],self.level_display_pos[1]+50
        
    def random_color(self):
        for i in range(1,8,1):
            self.cell_colors[i]=[randint(0,255) for _ in range(3)]
            
    def get_cell_color(self,cell):
        #cell is brick marker
        if self.black_cell:
            return self.black_cell_color
        else:
            if cell in self.cell_colors:
                return self.cell_colors[cell]
            return self.black_cell_color
conf= Config()

class PytrisError(Exception):
    pass

class Block():
    """Tetris block generation and modification
    
    Arguments:
    grid_size -- length of a square 2d grid.
    grid -- 2d grid.
    
    Block contains a 2d grid. Size of this grid will depends on given 
    coordination list. `list_to_grid` method convert given list to a grid
    from given grid size. To get exact grid size use `calc_grid_size` method
    
    Here is an example of `L` block.
    >>> marker = 1
    >>> l_coords_list = [(0,1),(1,1),(2,1),(2,0)]
    >>> l_grid_size = Block.calc_grid_size(l_coords_list) #3
    >>> l_grid=Block.list_to_grid(l_coords_list,l_grid_size,marker)
    >>> L_Block = Block(l_grid_size, l_grid)
    >>> print(L_Block.grid)
    [
        [0,0,1],
        [1,1,1],
        [0,0,0]
    ]
    
    Here 0 is empty and 1(marker) is brick of a block. Non-empty brick marker can 
    be anything between 0<marker<100. Tetris has classic seven blocks, different 
    value can represent different block type and later can be used to assign color.
    In `conf.cell_colors` there are colors for seven types of block.
    Assigning this values to l_block's grid and grid_size  will make a complete block.
    
    Simplify this proccess by using `from_list` classmethod.
    To make classic tetris block use `from_classic` classmethod.
    """ 
    def __init__(self,grid_size,grid):
        self.grid_size = grid_size
        self.grid = grid
    
    def __iter__(self):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                yield (x,y,self[x,y])
                
    def __str__(self):
        string = ""
        for row in self.grid:
            for brick in row:
                if brick:
                    if conf.debug: string+=f"{brick},"
                    else: string+=f"{conf.ascii_repr_char} "
                else:
                    if conf.debug: string+=f"{brick},"
                    else: string+=". "
            string+="\n"
        return string

    def __getitem__(self,xy):
        x,y = xy
        return self.grid[y][x]
        
    @staticmethod
    def calc_grid_size(coords):
        max_x, max_y = 0,0
        for x,y in coords:
            max_x = max(max_x,x)
            max_y = max(max_y,y)
        return max(max_x,max_y)+1
        
    @staticmethod    
    def list_to_grid(coords,grid_size,marker):
        temp_grid = [[0]*grid_size for _ in range(grid_size)]
        for x,y in coords:
            temp_grid[y][x]=marker
        return temp_grid
    
    @classmethod
    def from_list(cls,coords, marker):
        """Return instance of a Block, generated from given coords and marker
        
        Arguments:
        coords -- list of (x,y) coordinations
        marker -- Block's brick identity
        """
        grid_size = Block.calc_grid_size(coords)
        grid = Block.list_to_grid(coords,grid_size,marker)
        return cls(grid_size,grid)
    
    @classmethod
    def from_classic(cls,name=None):
        """Return instance of a Block contains one of the seven classic tetris block
        
        Keyword Arguments:
        name -- name of a classic tetris block. valid names are ["L","J","Z","S","I","T","O"]
        """
        names = ["L","J","Z","S","I","T","O"]
        if not name:
            if conf.debug_block_type: #debug mode
                name = conf.debug_block_name #always spawn this type of block
            else:#name is not given so choosing random one
                name = choice(names) #Not that good randomness.
        else:
            name = name.upper() #validity check
            
        coords = None
                                              #
        if name=="L":       #orange ricky   ###
            coords=[(0,1),(1,1),(2,1),(2,0)]
                                            #
        elif name=="J":     #blue ricky     ###
            coords=[(0,0),(0,1),(1,1),(2,1)]
                                            ##
        elif name=="Z":     #cleveland z     ##
            coords=[(0,0),(1,0),(1,1),(2,1)]
                                              ##
        elif name=="S":     #rhode island z  ##
            coords=[(1,0),(2,0),(0,1),(1,1)]
        
        elif name=="I":     #hero           ####
            coords=[(0,1),(1,1),(2,1),(3,1)]
                                             #
        elif name=="T":     #teewee         ###
            coords=[(1,0),(0,1),(1,1),(2,1)]
                                            ##
        elif name =="O":    #smashboy       ##
            coords=[(0,0),(1,0),(0,1),(1,1)]
        else:
            raise PytrisError(f"'{name}' is not a valid classic tetris block type")
            
        #0 marker means empty brick. but L piece is at 0 in names.
        marker = names.index(name)+1 #so making index starts from 1
        grid_size = Block.calc_grid_size(coords)
        grid = Block.list_to_grid(coords,grid_size,marker)
        
        return cls(grid_size,grid)
        
    @classmethod
    def from_random(cls,grid_size, marker):
        """Not yet implemented"""
        
    def rotate(self,clockwise=0):
        """clockwise or counter clockwise rotation at 90 degree"""
        new_grid = [[0]*self.grid_size for _ in range(self.grid_size)]
        for a,b,marker in self:
            #a is increasing before b, self[b][a] is marker
            #so reading from left to right direction of self
            if clockwise: #rotate clockwise
                pointer = self.grid_size-1-b #pointer = x, right of the grid
                #writing from right top corner to bottom direction, a = y
                new_grid[a][pointer] = marker
            else:
                pointer = self.grid_size-1-a #pointer = y, bottom of the grid
                #writing from left bottom corner to top, b=x
                new_grid[pointer][b] = marker 
        #rotating but not commiting because rotate can fail.
        #later this Block can be used to commit rotation
        return Block(self.grid_size,new_grid)
        

class TetrisCollision():
    def __init__(self,type_,boolean):
        self.type = type_
        self.bool = boolean
    def __bool__(self):
        return self.bool

class TetrisEngine():
    """Main Tetris grid contains all bricks and handle collision.
    
    Arguments:
    x -- size of Tetris grid in x axis
    y -- size of Tetris grid in x axis
    
    >>>tetrisEngine = TetrisEngine(10,20) #classic tetris grid size
    a (10,20) tetris grid
    
    0 0 0 0 0 0 0 0 0 0  -> p3
    0 0 0 0 0 0 0 0 0 0         
    0 0 0 0 0 0 0 0 0 0         
    0 0 0 0 0 0 0 0 0 0         
    0 0 0 0 0 0 0 0 0 0         
    0 0 0 0 0 0 0 7 7 0  -> p4
    0 0 0 0 0 0 0 7 7 0         
    0 0 0 0 0 0 0 0 0 0               
    0 0 1 0 6 0 0 0 0 0  -> p2
    1 1 1 6 6 6 5 5 5 5  -> p1
    
    p1: `row_check` method says this row has filled up
    -1: removing this row will misplaced any active block position
    -2: So remove active block by `clear_block` method
    -3: Now remove this row (y=self.h-1)
    p2: this row will be last row after p1 action
    
    p3: After p1 insert empty row here (y=0) to maintain grid height as it was before. 
    -1: at y there can be an active block which is going down.
    -2: But because it has removed so it will not make any effect 
    -3: then restore active block by using `place_block` method
    
    p4: A block is going down. use `move` or `rotate` method to make changes. But before that check if that is possible
    -1: Use `collision` method to detect any collision. collision types are 'wall', 'brick' or 'floor'
    -2: if `rotate` is not possible perform variation of rotation using `rotate_kick` method
    
    p5: After p4 use `collision_handler` to determine what to do 
    -1: `move` method will not do movement if collision occured.
    -2: if `move` is downward and collision.type = 'brick' or 'floor'
    -3: collision_handler` will fixed the block at current position or call gameover.
    -4: if gameover run cleanup steps using `game_cleanup` method.
    """
    def __init__(self,x,y):
        self.w = x
        self.h = y
        
        self.grid = [[0]*x for _ in range(y)]
        
        self.block = Block.from_classic() #current block in action
        self.next_block = Block.from_classic()
        
        #start at above grid y=0
        #All block position related method use this variable to determine position of a block
        #Modifying this variable will modify position of a block.
        self.block_pos = conf.spawn_point,-3 
        
        self.space_available = True #used to determine game over or not
        self.non_zero_rows = [] #index of filled up rows , remove and add score
        
        self.debug_cells = []
        self.need_to_clean_row = -1
    
    def __str__(self):
        string = ""
        for row in self.grid:
            for brick in row:
                if brick:
                    if conf.debug: string+=f"{brick},"
                    else: string+=f"{conf.ascii_repr_char} "
                else:
                    if conf.debug: string+=f"{brick},"
                    else: string+=". "
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
                
    def debug_brick(self,x,y,value=100):
        """Place a single brick on main grid at given x,y for testing"""
        if conf.debug:
            self[x,y] = value
    
    def place_block(self):
        """Place a block in tetris grid at x,y position.
        
        Top left corner of a Block is the anchor point. So top left corner
        brick will be in x,y position other bricks of that block will 
        be in increment of x and y position"""
        pos_x, pos_y = self.block_pos #given position
        for x,y,marker in self.block: #reading from top left of the block
            #a block can be outside of the main grid. e.g At first spawn  y<0
            #Then sometimes it appear bottom of the grid. e.g. >>> l=[0,1,2,] >>> l[-1] # 2
            if marker and pos_y+y>=0: #prevent that
                if conf.debug_placement:
                    print(f"place_block at : {pos_x+x},{pos_y+y}")
                self.grid[pos_y+y][pos_x+x] = marker
            else:
                if conf.debug: #storing empty cells too
                    self.debug_cells.append((pos_x+x,pos_y+y))
    
    def clear_block(self):
        """Remove a block from main grid.
        
        `place_block` method puts bricks on main Grid, If brick move to 
        a new position then previous position's bricks will remain there and make a trail. 
        Besides `collision` method will collide with own bricks if not cleared"""
        pos_x, pos_y = self.block_pos
        for x,y,marker in self.block:
            if marker and pos_y+y>=0:
                self.grid[pos_y+y][pos_x+x] = 0
        if conf.debug:
            self.debug_cells=[]
        
    def row_check(self):
        """Loop through last brick position to check if that block filled up any row.
        If true store that in `self.non_zero_rows` to handle it later."""
        self.non_zero_rows = []
        #A non zero row can be only there where last block placed.
        #y of last placed block
        _,y_begin = self.block_pos 
        y_end = y_begin+self.block.grid_size #numbers of row covered by a block
        for y in range(y_begin,y_end+1,1):
            if y<self.h: #block anchor is top left corner, so placed y position can be greater than h
                if 0 not in self.grid[y]:
                    self.non_zero_rows.append(y)
    
    def move(self,direction):
        """Control movements of a block in tetris grid
        
        Arguments:
        direction -- the direction a block will move. 'r','l','u','d' are valid option
        """
        position = self.block_pos
        pos_x, pos_y = position
        self.clear_block() #prevent movement trail effects.
        if direction=="r": #right
            position = pos_x+1, pos_y
        elif direction=="l": #left
            position = pos_x-1, pos_y
        elif direction == "d": #down
            position = pos_x, pos_y+1
        elif direction == "u": #up only for debug
            position = pos_x, pos_y-1
        else:
            raise PytrisError(f"'{direction}' is not a valid move")
        #Check if new position is possible for a block to move.
        if not (collision:=self.collision(self.block, *position)) and self.space_available:
            #no collision occured.
            #so updating block_pos with new one because it is possible to move
            self.block_pos = position 
        else:
            #Collision occured so passing collision data and 
            #the direction it happened to handler method
            self.collision_handler(collision,direction)
        #If collision block_pos will remain same. so it will place the block as it was before
        self.place_block()
        
    def translate_rotate(self,rotated_block,clockwise):
        """Not Yet implemented""" #TODO https://tetris.wiki/Super_Rotation_System
                    
    def rotate(self,clockwise=1):
        self.clear_block()
        #rotation is not always possible, before rotating self.block
        #first making a duplicate of that block with rotation.
        rotated_block= self.block.rotate(clockwise)
        if not self.collision(rotated_block,*self.block_pos) and self.space_available:
            #rotation is possible at current position
            self.block = rotated_block #so now commiting the change to self.block
        else:
            #Some variation of rotation can be successful. Testing those variation here
            if conf.rotation_kick:
                self.translate_rotate(rotated_block,clockwise)
        self.place_block()
        
    def collision(self,block_obj,x,y):
        """Check collision of a block at given x,y position in tetris grid"""
        for bx,by,marker in block_obj:
            if marker: #Rejecting empty marker
                #Brick is outside of tetris grid in x direction
                if not 0<=bx+x<self.w:
                    return TetrisCollision("wall",True) #collided with side wall
                elif by+y>=self.h: #self.h is the floor
                    return TetrisCollision("floor",True) #collided with brick
                elif by+y>=0 : #within tetris grid area.
                    if self[bx+x,by+y]: #so check if there is any brick
                        return TetrisCollision("brick",True) #collided with brick
        
        return False #no collision
        
    def collision_handler(self,collision,current_move):
        """determines what to do with collision"""
        if conf.debug:
            print(f"Collision type : {collision.type}")
        if current_move == "d":
            #downward movement occured and faced a brick or floor
            if collision.type =="brick" or collision.type=="floor":
                #so no more movement is possible at all.
                #There are two things to do now
                _,y = self.block_pos
                if y<0: #So the block can not even enter the tetris grid
                    #so no more space is available. it is gameover actually.
                    self.space_available=False
                    self.need_to_clean_row=self.h-1
                else:
                    self.place_block() #block is placed
                    self.row_check()  #checking if this block complete a grid
                    #previous block is now fixed,
                    #Spawning New block (which is previously generated and kept in next_block)
                    self.block = self.next_block 
                    self.block_pos = conf.spawn_point,-3
                    self.next_block = Block.from_classic() #random next block
                    
    def reset(self):
        self.block = Block.from_classic()
        self.next_block = Block.from_classic()
        self.block_pos = conf.spawn_point,-3
        
    def game_over_cleanup(self):
        if 0<=self.need_to_clean_row<self.h:
            self.grid.pop(self.need_to_clean_row)
            self.grid.insert(self.need_to_clean_row,[0]*self.w)
            self.need_to_clean_row -=1
            self.debug_cells = []
        
class Tetris():
    """Tetris gameplay and interface"""
    def __init__(self,pygame_screen):
        self.screen = pygame_screen
        
        self.engine = TetrisEngine(conf.grid_w,conf.grid_h)
        self.engine.place_block() #placing initial block
        
        self.cell_dim = conf.cell_size+conf.cell_gap #cell dimension with gap
        
        self.grid_x, self.grid_y = conf.grid_display_pos
        rect_x = self.grid_x - self.grid_x/3
        rect_y = self.grid_y - self.grid_y/3
        self.grid_bg_rect = rect_x,rect_y,conf.screen_w - (rect_x*2), conf.grid_h * self.cell_dim + rect_y
        self.nblock_x,self.nblock_y = conf.next_block_display_pos
        
        
        #game state
        self.game_stop = True
        self.score =0
        self.level = conf.starting_level
        if self.level < 0:
            raise PytrisError(f"{conf.starting_level} - level can not be smaller than 0")
        self.line_cleared = 0
        self.game_speed = conf.base_speed / (self.level+1)
        
        
        
        self.font = pygame.font.SysFont("monospace",30)
        self.score_srf = self.font.render(f"{self.score}",1,(0,0,0))
        self.level_srf = self.font.render(f"lvl {self.level}",1,(0,0,0))
        self.line_srf = self.font.render(f"ln  {self.line_cleared}",1,(0,0,0))
        
        self.game_over_srf = self.font.render("Game Over",2,(0,0,0))
        srf_x,srf_y = self.game_over_srf.get_size()
        self.game_over_display_pos = self.grid_x+conf.grid_pw/2 - srf_x/2,conf.grid_ph/2 - srf_y/2 + self.grid_y
        
        self.start_srf = self.font.render("Press Down key",2,(0,0,0))
        srf_x,srf_y = self.start_srf.get_size()
        self.start_display_pos = self.grid_x+conf.grid_pw/2 - srf_x/2,conf.grid_ph/2 - srf_y/2 + self.grid_y
        
        self.pytris_srf = self.font.render("Pytris",2,(0,0,0))
        srf_x,srf_y = self.pytris_srf.get_size()
        self.pytris_display_pos = self.grid_x+conf.grid_pw/2 - srf_x/2,conf.grid_ph/3 - srf_y/2 + self.grid_y
        
        #speed clock
        self.game_clock = pygame.time.Clock()
        self.time_passed = 0
        
        #animation
        self.animation_clock = None
        self.non_zero_remove_time = 0
        self.tetris_boom = False
        
    def score_and_level(self,nzr_n):
        if nzr_n == 1:
            self.score += (conf.score_base-10) * (self.level+1)
        else:
            self.score += conf.score_base*(math.factorial(nzr_n))*(self.level+1)
        
        self.score_srf = self.font.render(f"{self.score}",1,(0,0,0))
        
        self.line_cleared += nzr_n
        self.line_srf = self.font.render(f"ln  {self.line_cleared}",1,(0,0,0))
        
        if conf.level_up_by_score:
            if abs(self.level-conf.starting_level)<int(self.score/conf.level_up_score):
                self.level+=1
                self.level_srf = self.font.render(f"lvl {self.level}",1,(0,0,0))
                self.game_speed = conf.base_speed / (self.level+1)
        else: #level up by line cleared
            if abs(self.level-conf.starting_level)<int(self.line_cleared/conf.level_up_line):
                self.level+=1
                self.level_srf = self.font.render(f"lvl {self.level}",1,(0,0,0))
                self.game_speed = conf.base_speed / (self.level+1)
        if conf.debug_score_and_level:
            print(f"score : {self.score}, level : {self.level}, line : {self.line_cleared}")
        
    def nzr_handle(self):
        """Animate and remove non zero rows from main grid"""
        nzr = self.engine.non_zero_rows #number of rows without empty brick
        if nzr: #nzr>0
            if not self.animation_clock:
                self.animation_clock=pygame.time.Clock()
                self.tetris_boom = True if len(nzr)==4 else False
            self.non_zero_remove_time+= self.animation_clock.tick()/1000
            if self.non_zero_remove_time>conf.boom_duration:
                self.engine.clear_block() #before removing row removing active block
                nzr_n = 0
                for y in nzr:
                    self.engine.grid.pop(y) #removing y row
                    self.engine.grid.insert(0,[0]*self.engine.w) #adding empty row
                    nzr_n +=1
                self.score_and_level(nzr_n)
                self.engine.place_block()
                self.engine.non_zero_rows=[]
                self.non_zero_remove_time=0
                self.animation_clock= None
                self.tetris_boom= False
    def move(self,direction):
        if not self.game_stop:
            self.engine.move(direction)
            
    def rotate(self,clockwise=1):
        if not self.game_stop:
            self.engine.rotate(clockwise)
            
    def rand_color(self,begin=0,end=255):
        if conf.black_cell:
            return [randint(begin,end)]*3
        return [randint(begin,end) for _ in range(3)]
        
    def draw_cell(self,x,y,cell,pos_x,pos_y,draw_inactive=1,non_zero=False,debug_cells=()):
        points = pos_x+(self.cell_dim)*x,pos_y+(self.cell_dim)*y,conf.cell_size,conf.cell_size
        if 0<cell<100:
            color = conf.get_cell_color(cell)
            if non_zero: #non zero row, removing animation
                pygame.draw.rect(self.screen,self.rand_color(begin=180),points)
            else:
                pygame.draw.rect(self.screen,color,points)
                
            if conf.draw_cell_border:
                if conf.black_cell:
                    pygame.draw.rect(self.screen,(20,20,20),points,width=1)
                else:
                    pygame.draw.rect(self.screen,(30,40,30),points,width=1)
        elif cell==100: #debug cell
            pygame.draw.rect(self.screen,(255,0,0),points)
        else:
            if draw_inactive: #empty cell marker = 0
                pygame.draw.rect(self.screen,conf.inactive_cell_color,points)
            if conf.debug:
                if (x,y) in debug_cells:
                    pygame.draw.rect(self.screen,(255,0,255),points)
    
    def render(self):
        if self.tetris_boom: #boom bg blink animation
            pygame.draw.rect(self.screen, self.rand_color(200,220), self.grid_bg_rect)
        else:
            pygame.draw.rect(self.screen, conf.grid_bg, self.grid_bg_rect)
            
        pygame.draw.rect(self.screen, conf.border_bg, self.grid_bg_rect,width=2)
        
        for x,y,marker in self.engine: 
            if y in self.engine.non_zero_rows: #filled up row, blinking animation
                self.draw_cell(x,y,marker,self.grid_x,self.grid_y,non_zero=True,debug_cells=self.engine.debug_cells)
            else: #normal color
                self.draw_cell(x,y,marker,self.grid_x,self.grid_y,debug_cells=self.engine.debug_cells)
        if not self.game_stop:
            for x,y,cell in self.engine.next_block:
                self.draw_cell(x,y,cell,self.nblock_x,self.nblock_y,0)
        self.screen.blit(self.score_srf,conf.score_display_pos)
        self.screen.blit(self.level_srf,conf.level_display_pos)
        self.screen.blit(self.line_srf,conf.line_display_pos)
        
        if not self.engine.space_available:
            self.screen.blit(self.game_over_srf,self.game_over_display_pos)
        if self.game_stop:
            self.screen.blit(self.pytris_srf,self.pytris_display_pos)
            self.screen.blit(self.start_srf,self.start_display_pos)

    def restart(self):
        self.game_stop = False
        self.engine.space_available=True
        self.engine.reset()
        self.animation_clock = None
        self.tetris_boom = False
        
        self.level = conf.starting_level
        self.score =0
        self.line_cleared = 0
        self.game_speed = conf.base_speed / (self.level+1)
        
        self.score_srf = self.font.render(f"{self.score}",2,(0,0,0))
        self.level_srf = self.font.render(f"lvl {self.level}",2,(0,0,0))
        self.line_srf = self.font.render(f"ln  {self.line_cleared}",1,(0,0,0))
        self.non_zero_remove_time = 0
        
        self.engine.need_to_clean_row = conf.grid_h-1
        
    def cycle(self):
        if not self.game_stop:
            if self.engine.space_available:
                self.time_passed+= self.game_clock.tick()/100 
                if self.time_passed>self.game_speed:
                    if conf.debug_tetris_grid:
                        print(self.engine)
                    if not conf.debug_stop_falling:
                        self.engine.move("d")
                    self.time_passed = 0
                self.nzr_handle()
            elif self.engine.need_to_clean_row!=-1: #no space available or restart
                self.time_passed+= self.game_clock.tick()/1000
                if self.time_passed>0.1:
                    self.engine.game_over_cleanup()
                    self.time_passed = 0
            else:
                self.game_stop = True
                #engine cleaned
                self.engine.space_available = True
        self.render()
        
        
def play():
    screen = pygame.display.set_mode((conf.screen_w,conf.screen_h))
    game = Tetris(screen)
    key_clock=pygame.time.Clock()
    
    pressed_key = None
    pressed_time = 0
    
    
    def key_press(key):
        if conf.key_pressed_hold:
            return key
        else:
            game.move(key)
            return None
        
    while True:
        screen.fill(conf.bg)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYUP:
                pressed_key=None
            if event.type == pygame.KEYDOWN:
                if event.key == 1073741903:   #right
                    pressed_key=key_press('r')
                elif event.key == 1073741904: #left
                    pressed_key=key_press('l')
                elif event.key == 1073741905: #down
                    if game.game_stop:
                        game.restart()
                    pressed_key=key_press('d')
                elif event.key == 1073741906: #up
                    if conf.debug:
                        game.move('u')
                    else:
                        game.rotate(1) #clockwise
                    
                elif event.unicode == 'a': #rotate
                    game.rotate(0)#counter clockwise
                elif event.unicode == 's': #rotate
                    game.rotate(1)#clockwise
                elif event.unicode == 'c': #change theme
                    conf.black_cell = not conf.black_cell
                elif event.unicode ==']': #increase level
                    if game.game_stop:
                        conf.starting_level+=1
                        game.level_srf = game.font.render(f"lvl {conf.starting_level}",1,(0,0,0))
                elif event.unicode =='[': #decrease level
                    if game.game_stop and conf.starting_level>0:
                        conf.starting_level-=1
                        game.level_srf = game.font.render(f"lvl {conf.starting_level}",1,(0,0,0))
                
                elif event.unicode =="r":
                    if not game.game_stop:
                        game.engine.space_available=False
                    
                    
        if pressed_key:
            pressed_time += key_clock.tick()/1000
            if pressed_key=="d":
                if pressed_time>0.05:
                    game.move(pressed_key)
                    pressed_time = 0
            else:
                if pressed_time>0.1:
                    game.move(pressed_key)
                    pressed_time = 0
                    
        game.cycle()
        pygame.display.flip()
        
if __name__=="__main__":
    if (in_android:=not True):
        conf.set_screen(720,1440)
        conf.key_pressed_hold=False
    else:
        conf.set_screen(500,650)
        
    conf.starting_level=0
    conf.base_speed=10
    play()
