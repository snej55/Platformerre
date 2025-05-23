# Platformerre
This project is a vfx demo and further test for my pygame (pygame-ce) framework (Pygmy? no name yet). So far it utilizes mainly my framework for handling entities, collisions, grass and other various vfx. This project (although a simple platformer) will hopefully allow me to continue to update and expand my framework to include stuff such as water, cloth physics with verlet integration and ui. These have not been added yet. See: [Fishipus](https://github.com/snej55/Fishipus)

## Run:

Do the following:
```
# clone the repo
git clone https://github.com/snej55/Platformerre
cd Platformerre

# install the required packages
pip3 install -r requirements.txt

# run
python3 main.py
```

# What does my framework do now?
*description taken from Fishipus repository*
It will handle physics, entity management, camera, animation, particle systems, ui, loading assets, tile and chunk systems, shaders (moderngl), rendering, audio and more; it will be able to be 'plugged' in to a project, or you can start a project from this so that you just have to add minimal code & graphics, etc and have a fast, working game (and be done with it). Also implemented is a module for shaders - using moderngl - which allows you to just write a fragment & a vertex shader and not have to worry about all the opengl stuff behind the scenes. For the entity management & physics, you can just inherit from the parent Entity class which handles rendering, physics and animation, and (if it is not the player) it will be automatically added to the EntityManager's entities. The EntityManager handles updating & rendering the entities, and uses a system of chunks/quads to optimise this. In the .__init__ method of each Entity (if it is not the player) the entity will add itself to the entity manager. As for tiling and decor, there is a TileMap object, which includes the different layers and a PhysicsMap (as the name suggests, this is for collisions). Per layer, tile data is stored in a dictionary, and there is a chunk system in place for offgrid tiles. There is a built in level editor for - you guessed it - editing levels (beware, however as if you venture into the source code of the editor, you will be confronted with some of the *stinkiest* code you will ever see in this project: I suggest you wash your hands after editing). The level data is stored in *.json* files, and is loaded by the TileMap() class. I already had a basic system in place for grass & water, but these still need a lot of work. For both of them they need to be *optimised to oblivion* as they currently will nuke the performance if too much is added. For the grass, I am working on efficient image caching (I had this in place, but even if the images are not being dynamically generated, it is still to slow to blit hundreds of images to the screen). Solving this should involve doing it in tiles, etc but I can't really be bothered at the moment. As for the water, there were some issues generating it, and it was - as well - not very performant. 

The engine also has a particle system in place, with various *misc* gfx options. There are sparks, smoke, shockwaves, impact lines in the gfx manager. This is all aranged in the GFXMangager() class. The manager also handles various physics particles, with there being a special class for the ones with special fx. The transparent particles and vfx are rendered to a seperate alpha_surf which is then passed into the fragment shader. The fragment shader then renders this surface onto the main texture, which would be the equivalent of passing the pygame.BLEND_RGBA_ADD flag to the surf.blit() function. This means that I just have to change the color of the surface, instead of setting and rendering an alpha for each particle. This gives a decent performace boost (especially for the particles with trails).
