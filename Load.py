import glfw
from OpenGL.GL import *
import numpy as np
import glm
from PIL import Image
from PIL._imaging import display


def load_model_from_file(filename):
    """Loads a Wavefront OBJ file. """
    objects = {}
    vertices = []
    texture_coords = []
    faces = []

    material = None

    # abre o arquivo obj para leitura
    for line in open(filename, "r"):  ## para cada linha do arquivo .obj
        if line.startswith('#'): continue  ## ignora comentarios
        values = line.split()  # quebra a linha por espaço
        if not values: continue

        ### recuperando vertices
        if values[0] == 'v':
            if values[1:4] not in vertices:
                vertices.append(values[1:4])


        ### recuperando coordenadas de textura
        elif values[0] == 'vt':
            texture_coords.append(values[1:3])

        ### recuperando faces
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'f':
            face = []
            face_texture = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 2 and len(w[1]) > 0:
                    face_texture.append(int(w[1]))
                else:
                    face_texture.append(0)

            faces.append((face, face_texture, material))

    model = {}
    model['vertices'] = vertices
    model['texture'] = texture_coords
    model['faces'] = faces

    return model


def load_texture_from_file(texture_id, img_textura):
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    img = Image.open(img_textura)
    img_width = img.size[0]
    img_height = img.size[1]
    image_data = img.tobytes("raw", "RGB", 0, -1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_width, img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)


def load_object(vertices_list, textures_coord_list, obj_filename, texture_filenames, obj_id):
    modelo = load_model_from_file(obj_filename)
    retornos = [[len(vertices_list), 0]]
    print('Processando modelo cube.obj. Vertice inicial:', len(vertices_list))
    text = modelo['faces'][0][2]
    text2 = ""
    texture_counter = 1
    print(text)
    for face in modelo['faces']:
        if text != face[2]:
            text = face[2]
            retornos[texture_counter - 1][1] = len(vertices_list) - 1
            texture_counter += 1
            retornos.append([len(vertices_list), 0])

        for vertice_id in face[0]:
            vertices_list.append(modelo['vertices'][vertice_id - 1])
        for texture_id in face[1]:
            textures_coord_list.append(modelo['texture'][texture_id - 1])
    retornos[texture_counter - 1][1] = len(vertices_list)
    for i in range(0, len(texture_filenames)):
        load_texture_from_file(obj_id + i, texture_filenames[i])
    return retornos
