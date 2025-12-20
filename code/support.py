from csv import reader
from os import walk
import pygame

def import_csv_layout(path):
    """
    Lê um arquivo CSV (mapa do Tiled) e retorna uma matriz (lista de listas).
    """
    terrain_map = []
    try:
        with open(path) as map_file:
            level = reader(map_file, delimiter=',')
            for row in level:
                terrain_map.append(list(row))
    except FileNotFoundError:
        print(f"ERRO: Não encontrei o arquivo em {path}")
        return [] 
    return terrain_map

def import_folder(path, target_height=None):
    surface_list = []

    for _, __, img_files in walk(path):
        img_files.sort() 
        for image_name in img_files:
            full_path = path + '/' + image_name
            try:
                image_surf = pygame.image.load(full_path).convert_alpha()
                
                if target_height:
                    original_width = image_surf.get_width()
                    original_height = image_surf.get_height()
                    
                    ratio = target_height / original_height
                    new_width = int(original_width * ratio)
                    new_height = int(target_height)
                    
                    image_surf = pygame.transform.scale(image_surf, (new_width, new_height))

                surface_list.append(image_surf)
            except Exception as e:
                print(f"Erro ao carregar imagem: {full_path} | {e}")
            
    return surface_list

def import_character_assets(path, target_height=None):
    animations = {}
    directions = ['up', 'down', 'left', 'right']

    for direction in directions:
        full_path = path + direction
        
        animations[direction] = import_folder(full_path, target_height)
        
        idle_key = direction + '_idle'
        
        if len(animations[direction]) > 0:
            animations[idle_key] = [animations[direction][0]]
        else:
            animations[idle_key] = [] 
            
    return animations