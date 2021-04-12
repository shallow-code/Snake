import pyglet
import pyglet.clock
import random
from pyglet.window import key

# CYCLIC MAP?
cyclic_map = True

#start
main_batch = pyglet.graphics.Batch()
Scale_game = 3
delta = 11 * Scale_game
n_celle_x = 20
n_celle_y = 20
window_height = n_celle_y * delta
window_width = n_celle_x * delta
#create grid of all possible cooridinates
grid_xy=[]
for i in range(n_celle_x):
    for j in range(n_celle_y):
        grid_xy.append([delta*i+delta//2 ,delta*j+delta//2])
#create game window
game_window = pyglet.window.Window(window_width, window_height)


#path
pyglet.resource.path=['./resources']
pyglet.resource.reindex()
#load img
im_segment_body = pyglet.resource.image("body_snake.png")
im_food = pyglet.resource.image("food.png")

#center img
def center_im(image):
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
center_im(im_segment_body)
center_im(im_food)

#CLASS
#head Snake
class Head_snake(pyglet.sprite.Sprite):
    
    def __init__(self, *args, **kwargs):
        super().__init__(img=im_segment_body, *args, **kwargs)
        self.scale = Scale_game
        self.direction_x = 1
        self.direction_y = 0
        self.old_direction_x = 1
        self.old_direction_y = 0
        self.alive = True
        

    #keys, devo trovare un modo premerlo 1 volta per FRAME!!!!!!!!!!!!!!!!!!!!!!!
    def on_key_press(self, symbol, modifiers):
        if symbol==key.UP:
            if not (self.old_direction_x == 0 and self.old_direction_y == -1):
                self.direction_x = 0
                self.direction_y = 1
        if symbol==key.DOWN:
            if not (self.old_direction_x == 0 and self.old_direction_y == 1):
                self.direction_x = 0
                self.direction_y = -1
        if symbol==key.LEFT:
            if not (self.old_direction_x == 1 and self.old_direction_y == 0):
                self.direction_x = -1
                self.direction_y = 0
        if symbol==key.RIGHT:
            if not (self.old_direction_x == -1 and self.old_direction_y == 0):
                self.direction_x = 1
                self.direction_y = 0
        
    #movement
    def update(self,dt):
        if self.alive:
            #memo last directions
            self.old_direction_x = self.direction_x
            self.old_direction_y = self.direction_y
            
            if cyclic_map:
                self.x = (((self.x - delta//2)/delta + self.direction_x) % n_celle_x)*delta +delta//2
                self.y = (((self.y - delta//2)/delta + self.direction_y) % n_celle_y)*delta +delta//2
            else:
                self.x += self.direction_x * delta
                self.y += self.direction_y * delta
                #hitting border and die
                if ((self.x<0 or self.x>window_width) or (self.y<0 or self.y>window_height)):
                    self.alive = False
        else:
            self.x += 0
            self.y += 0

    #check collision between food and snake
    def check_collision(self,other_obj):
        if ((self.x == other_obj.x) and (self.y == other_obj.y)):
            return True
        else:
            return False
            


#segment body
class body_snake(pyglet.sprite.Sprite):
    
    def __init__(self, *args, **kwargs):
        super().__init__(img=im_segment_body, *args, **kwargs)
        self.scale = Scale_game

    #movement
    def switch(self,other_obj):
        self.x = other_obj.x
        self.y = other_obj.y


#food
class Food(pyglet.sprite.Sprite):
    
    def __init__(self, *args, **kwargs):
        super().__init__(img=im_food, *args, **kwargs)
        self.scale = Scale_game
        #starting position without the line of the snake
        self.x = random.randint(0,n_celle_x-1)*delta+delta//2
        grid_y = [y for y in range(n_celle_y)]
        grid_y.remove(n_celle_y//2)
        n_cell_y = random.randint(0,n_celle_y-2)
        self.y = grid_y[n_cell_y]*delta+delta//2
        
    #create food
    def create_food(self,other_obj):
        #pop position taken by the snake for create the food
        remaining_xy = grid_xy[:]
        for pos in other_obj:
            remaining_xy.remove([pos.x ,pos.y])
        
        #radom position food
        n_pos = random.randint(0,len(remaining_xy)-1)   #choose random position
        self.x = remaining_xy[n_pos][0]
        self.y = remaining_xy[n_pos][1]
    


#Create Snake
#starting coord. head
n_seg_body = 4
points_score = 0
start_x = delta*(n_celle_x//2)+delta//2
start_y = delta*(n_celle_y//2)+delta//2
seg_head = Head_snake(x=start_x , y=start_y, batch=main_batch)
# body
body = [seg_head]
for i in range(n_seg_body):
    seg_body = body_snake(x=start_x - (i+1)*delta , y=start_y, batch=main_batch)
    body.append(seg_body)
#food
food = Food(batch=main_batch)


    
#EVENTS

@game_window.event
def on_key_press(symbol, modifiers):
    seg_head.on_key_press(symbol, modifiers)


#update positions starting from last segment
def update(dt):
    #segments
    for i in range(len(body)-1,0,-1):
        body[i].switch(body[i-1])
    #head
    seg_head.update(dt)

    #head-food interaction
    if seg_head.check_collision(food):
        food.create_food(body)
        seg_body = body_snake(x=body[n_seg_body].x , y=body[n_seg_body].y ,batch=main_batch)
        body.append(seg_body)

    #head-body interaction
    global points_score
    points_score = max(points_score,len(body)-5)
    for i in range(len(body)-1,0,-1):
        if seg_head.check_collision(body[i]):
            seg_head.alive = False
            #label death and score
            label_D = pyglet.text.Label('YOU DIED',
                                      font_name='Times New Roman',
                                      font_size=36/30 *min(n_celle_x,n_celle_y) * Scale_game,
                                      x=game_window.width//2, y=game_window.height//2,
                                      anchor_x='center', anchor_y='center',batch=main_batch)
            label_S = pyglet.text.Label('Score: ' + str(points_score),
                                      font_name='Times New Roman',
                                      font_size=20/30 *min(n_celle_x,n_celle_y) * Scale_game,
                                      x=game_window.width//2, y=0,
                                      anchor_x='center', anchor_y='bottom',batch=main_batch)

@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()


if __name__=='__main__':
    pyglet.clock.schedule_interval(update, 1/10.0)
    pyglet.app.run()
