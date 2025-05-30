# a bunch of constants
import pygame

from typing import TypeAlias, Union

Render: TypeAlias = list[str, tuple]
Vector: TypeAlias = Union[list[float], pygame.Vector2, pygame.Vector3]

SMOKE_DELAY = 3
CHUNK_SIZE = [20, 20]
ENTITY_QUAD_SIZE = [10, 10]
WATER_CHUNK_SIZE = [15, 15]
AUTO_TILE_TYPES = {"sand", "salt", "grass", "autumn", "rock", "wood"}
PHYSICS_TILE_TYPES = {"sand", "salt"}
DANGER = {'danger'} # don't change this
TILE_SIZE = 8
GRASS_DIM = (9, 9)
GRASS_DENSITY = 8
BLASER_CHUNK_SIZE = [10, 10]
GRASS_TENSION = 7
SOOT = (22, 19, 35)
GRASS_DAMPENING = 0.9
GRASS_ACCURACY = 2
WIN_DIMENSIONS = [400, 400]
TILE_CHUNK_SIZE = [20, 20]
RENDER_SCALE = 2.0
BASE_IMG_PATH = 'data/images'
BASE_AUDIO_PATH = 'data/audio'
AUTO_TILE_MAP = {'0011': 1, '1011': 2, '1001': 3, '0001': 4, '0111': 5, '1111': 6, '1101': 7, '0101': 8, 
                '0110': 9, '1110': 10, '1100': 11, '0100': 12, '0010': 13, '1010': 14, '1000': 15, '0000': 16}
NEIGHBOUR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (0, 0)]
KEYS = [
    pygame.K_BACKSPACE,
    pygame.K_TAB, 
    pygame.K_CLEAR,       
    pygame.K_RETURN,     
    pygame.K_PAUSE,       
    pygame.K_ESCAPE,      
    pygame.K_SPACE,       
    pygame.K_EXCLAIM,     
    pygame.K_QUOTEDBL,    
    pygame.K_HASH,       
    pygame.K_DOLLAR,      
    pygame.K_AMPERSAND,   
    pygame.K_QUOTE,       
    pygame.K_LEFTPAREN,   
    pygame.K_RIGHTPAREN,  
    pygame.K_ASTERISK,    
    pygame.K_PLUS,        
    pygame.K_COMMA,       
    pygame.K_MINUS,      
    pygame.K_PERIOD,      
    pygame.K_SLASH,       
    pygame.K_0,          
    pygame.K_1,         
    pygame.K_2,       
    pygame.K_3,         
    pygame.K_4,         
    pygame.K_5,         
    pygame.K_6,         
    pygame.K_7,         
    pygame.K_8,          
    pygame.K_9,         
    pygame.K_COLON,       
    pygame.K_SEMICOLON,   
    pygame.K_LESS,        
    pygame.K_EQUALS,      
    pygame.K_GREATER,     
    pygame.K_QUESTION,    
    pygame.K_AT,         
    pygame.K_LEFTBRACKET, 
    pygame.K_BACKSLASH,   
    pygame.K_RIGHTBRACKET,
    pygame.K_CARET,       
    pygame.K_UNDERSCORE,  
    pygame.K_BACKQUOTE,   
    pygame.K_a,          
    pygame.K_b,          
    pygame.K_c,          
    pygame.K_d,          
    pygame.K_e,          
    pygame.K_f,          
    pygame.K_g,          
    pygame.K_h,          
    pygame.K_i,         
    pygame.K_j,         
    pygame.K_k,          
    pygame.K_l,          
    pygame.K_m,         
    pygame.K_n,          
    pygame.K_o,          
    pygame.K_p,          
    pygame.K_q,          
    pygame.K_r,          
    pygame.K_s,          
    pygame.K_t,          
    pygame.K_u,          
    pygame.K_v,          
    pygame.K_w,          
    pygame.K_x,          
    pygame.K_y,          
    pygame.K_z,        
    pygame.K_DELETE,      
    pygame.K_KP0,     
    pygame.K_KP1,         
    pygame.K_KP2,         
    pygame.K_KP3,         
    pygame.K_KP4,         
    pygame.K_KP5,         
    pygame.K_KP6,         
    pygame.K_KP7,         
    pygame.K_KP8,         
    pygame.K_KP9,         
    pygame.K_KP_PERIOD,   
    pygame.K_KP_DIVIDE,   
    pygame.K_KP_MULTIPLY, 
    pygame.K_KP_MINUS, 
    pygame.K_KP_PLUS,    
    pygame.K_KP_ENTER,    
    pygame.K_KP_EQUALS,   
    pygame.K_UP,          
    pygame.K_DOWN,        
    pygame.K_RIGHT,       
    pygame.K_LEFT,        
    pygame.K_INSERT,      
    pygame.K_HOME,       
    pygame.K_END,        
    pygame.K_PAGEUP,      
    pygame.K_PAGEDOWN,    
    pygame.K_F1,         
    pygame.K_F2,         
    pygame.K_F3,         
    pygame.K_F4,         
    pygame.K_F5,         
    pygame.K_F6,         
    pygame.K_F7,         
    pygame.K_F8,         
    pygame.K_F9,         
    pygame.K_F10,        
    pygame.K_F11,        
    pygame.K_F12,        
    pygame.K_F13,        
    pygame.K_F14,       
    pygame.K_F15,       
    pygame.K_NUMLOCK,     
    pygame.K_CAPSLOCK,    
    pygame.K_SCROLLOCK,   
    pygame.K_RSHIFT,      
    pygame.K_LSHIFT,      
    pygame.K_RCTRL,       
    pygame.K_LCTRL,       
    pygame.K_RALT,        
    pygame.K_LALT,        
    pygame.K_RMETA,       
    pygame.K_LMETA,      
    pygame.K_LSUPER,      
    pygame.K_RSUPER,     
    pygame.K_MODE,        
    pygame.K_HELP,      
    pygame.K_PRINT,       
    pygame.K_SYSREQ,      
    pygame.K_BREAK,       
    pygame.K_MENU,      
    pygame.K_POWER,       
    pygame.K_EURO,        
    pygame.K_AC_BACK
]
