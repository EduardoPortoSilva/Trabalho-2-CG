#!/usr/bin/env python
# coding: utf-8

# # Aula 10.Ex1 - Modelo de Iluminação - Ambiente e Difusa

# ### Primeiro, importamos as bibliotecas necessárias.
# Verifique no código anterior um script para instalar as dependências necessárias (OpenGL e GLFW) antes de prosseguir.

# In[ ]:


import glfw
from OpenGL.GL import *
import numpy as np
import glm

from Load import *

glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
altura = 1600
largura = 1200
window = glfw.create_window(largura, altura, "Iluminação", None, None)
glfw.make_context_current(window)

vertex_code = """
        attribute vec3 position;
        attribute vec2 texture_coord;
        attribute vec3 normals;


        varying vec2 out_texture;
        varying vec3 out_fragPos;
        varying vec3 out_normal;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;        

        void main(){
            gl_Position = projection * view * model * vec4(position,1.0);
            out_texture = vec2(texture_coord);
            out_fragPos = vec3(position);
            out_normal = normals;
        }
        """

fragment_code = """

        uniform vec3 lightPos; // define coordenadas de posicao da luz
        uniform float ka; // coeficiente de reflexao ambiente
        uniform float kd; // coeficiente de reflexao difusa

        vec3 lightColor = vec3(1.0, 1.0, 1.0);

        varying vec2 out_texture; // recebido do vertex shader
        varying vec3 out_normal; // recebido do vertex shader
        varying vec3 out_fragPos; // recebido do vertex shader
        uniform sampler2D samplerTexture;



        void main(){
            vec3 ambient = ka * lightColor;             

            vec3 norm = normalize(out_normal); // normaliza vetores perpendiculares
            vec3 lightDir = normalize(lightPos - out_fragPos); // direcao da luz
            float diff = max(dot(norm, lightDir), 0.0); // verifica limite angular (entre 0 e 90)
            vec3 diffuse = kd * diff * lightColor; // iluminacao difusa

            vec4 texture = texture2D(samplerTexture, out_texture);
            vec4 result = vec4((ambient + diffuse),1.0) * texture; // aplica iluminacao
            gl_FragColor = result;

        }
        """

program = glCreateProgram()
vertex = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)

glShaderSource(vertex, vertex_code)
glShaderSource(fragment, fragment_code)

glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(vertex).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Vertex Shader")

glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(fragment).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Fragment Shader")

glAttachShader(program, vertex)
glAttachShader(program, fragment)

glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
    print(glGetProgramInfoLog(program))
    raise RuntimeError('Linking error')

glUseProgram(program)

glEnable(GL_TEXTURE_2D)
qtd_texturas = 10
textures = glGenTextures(qtd_texturas)

vertices_list = []
normals_list = []
textures_coord_list = []

model_files = [['house.obj', 'house.jpg'],['outhouse.obj','outhouse.png'],['table.obj', 'table.jpg']]
#model_files = [['table.obj', 'table.jpg']]
model_geometrical_init_infos = [{'r':[0.00001,0.00001,0.00001],'s':[.1,.1,.1],'t':[0,0,0], 'a':0,'kd':0.3,'ka':0.5},{'r':[0.00001,0.00001,0.00001],'s':[.1001,.1001,.1001],'t':[0,0,0], 'a':0,'kd':0.3,'ka':0.5},{'r':[0.00001,0.00001,0.00001],'s':[.1,.1,.1],'t':[0,0,0], 'a':0,'kd':0.3,'ka':0.5},{'r':[0.00001,0.00001,0.00001]}]
#model_geometrical_init_infos = [{'r':[0.00001,0.00001,0.00001],'s':[.1,.1,.1],'t':[0,0,0], 'a':0,'kd':0.3,'ka':0.5}]
model_infos = []
for idx, model_file in enumerate(model_files):
    modelo = load_model_from_file(model_file[0])
    initial_point = len(vertices_list)
    print(f'Processando modelo {model_file[0]}. Vertice inicial:', len(vertices_list))
    for face in modelo['faces']:
        for vertice_id in face[0]:
            vertices_list.append(modelo['vertices'][vertice_id - 1])
        for texture_id in face[1]:
            textures_coord_list.append(modelo['texture'][texture_id - 1])
        for normal_id in face[2]:
            normals_list.append(modelo['normals'][normal_id - 1])
    print(f'Processando modelo {model_file[0]}. Vertice final:', len(vertices_list))
    last_point = len(vertices_list)
    model_infos.append({'init':initial_point, 'last':last_point})
    load_texture_from_file(idx, model_file[1])

buffer = glGenBuffers(3)

vertices = np.zeros(len(vertices_list), [("position", np.float32, 3)])
vertices['position'] = vertices_list

glBindBuffer(GL_ARRAY_BUFFER, buffer[0])
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)
loc_vertices = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc_vertices)
glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)

textures = np.zeros(len(textures_coord_list), [("position", np.float32, 2)])  # duas coordenadas
textures['position'] = textures_coord_list

glBindBuffer(GL_ARRAY_BUFFER, buffer[1])
glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
stride = textures.strides[0]
offset = ctypes.c_void_p(0)
loc_texture_coord = glGetAttribLocation(program, "texture_coord")
glEnableVertexAttribArray(loc_texture_coord)
glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)

normals = np.zeros(len(normals_list), [("position", np.float32, 3)])  # três coordenadas
normals['position'] = normals_list

glBindBuffer(GL_ARRAY_BUFFER, buffer[2])
glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
stride = normals.strides[0]
offset = ctypes.c_void_p(0)
loc_normals_coord = glGetAttribLocation(program, "normals")
glEnableVertexAttribArray(loc_normals_coord)
glVertexAttribPointer(loc_normals_coord, 3, GL_FLOAT, False, stride, offset)

loc_light_pos = glGetUniformLocation(program, "lightPos")  # recuperando localizacao da variavel lightPos na GPU
glUniform3f(loc_light_pos, -1.5, 1.7, 2.5)  ### posicao da fonte de luz


cameraPos = glm.vec3(0.0, 0.0, 1.0);
cameraFront = glm.vec3(0.0, 0.0, -1.0);
cameraUp = glm.vec3(0.0, 1.0, 0.0);

polygonal_mode = False

ka_inc = 0.3
kd_inc = 0.5


def key_event(window, key, scancode, action, mods):
    global cameraPos, cameraFront, cameraUp, polygonal_mode
    global ka_inc, kd_inc

    cameraSpeed = 0.05
    if key == 87 and (action == 1 or action == 2):  # tecla W
        cameraPos += cameraSpeed * cameraFront

    if key == 83 and (action == 1 or action == 2):  # tecla S
        cameraPos -= cameraSpeed * cameraFront

    if key == 65 and (action == 1 or action == 2):  # tecla A
        cameraPos -= glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

    if key == 68 and (action == 1 or action == 2):  # tecla D
        cameraPos += glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

    if key == 80 and action == 1 and polygonal_mode == True:
        polygonal_mode = False
    else:
        if key == 80 and action == 1 and polygonal_mode == False:
            polygonal_mode = True

    if key == 265 and (action == 1 or action == 2):  # tecla cima
        ka_inc += 0.05

    if key == 264 and (action == 1 or action == 2):  # tecla baixo
        kd_inc += 0.05


firstMouse = True
yaw = -90.0
pitch = 0.0
lastX = largura / 2
lastY = altura / 2


def mouse_event(window, xpos, ypos):
    global firstMouse, cameraFront, yaw, pitch, lastX, lastY
    if firstMouse:
        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX = xpos
    lastY = ypos

    sensitivity = 0.3
    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw += xoffset;
    pitch += yoffset;

    if pitch >= 90.0: pitch = 90.0
    if pitch <= -90.0: pitch = -90.0

    front = glm.vec3()
    front.x = math.cos(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    front.y = math.sin(glm.radians(pitch))
    front.z = math.sin(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    cameraFront = glm.normalize(front)


glfw.set_key_callback(window, key_event)
glfw.set_cursor_pos_callback(window, mouse_event)


# ### Matrizes Model, View e Projection
#
# Teremos uma aula específica para entender o seu funcionamento.

# In[ ]:


def model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z):
    angle = math.radians(angle)

    matrix_transform = glm.mat4(1.0)  # instanciando uma matriz identidade

    # aplicando rotacao
    matrix_transform = glm.rotate(matrix_transform, angle, glm.vec3(r_x, r_y, r_z))
    # aplicando translacao
    matrix_transform = glm.translate(matrix_transform, glm.vec3(t_x, t_y, t_z))

    # aplicando escala
    matrix_transform = glm.scale(matrix_transform, glm.vec3(s_x, s_y, s_z))

    matrix_transform = np.array(matrix_transform)

    return matrix_transform


def view():
    global cameraPos, cameraFront, cameraUp
    mat_view = glm.lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
    mat_view = np.array(mat_view)
    return mat_view


def projection():
    global altura, largura
    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(45.0), largura / altura, 0.1, 1000.0)
    mat_projection = np.array(mat_projection)
    return mat_projection


# ### Nesse momento, exibimos a janela.

# In[ ]:


glfw.show_window(window)
glfw.set_cursor_pos(window, lastX, lastY)

# ### Loop principal da janela.
# Enquanto a janela não for fechada, esse laço será executado. É neste espaço que trabalhamos com algumas interações com a OpenGL.

# In[ ]:


import math

glEnable(GL_DEPTH_TEST)  ### importante para 3D

ang = 0.0

while not glfw.window_should_close(window):

    glfw.poll_events()

    ang += 0.005

    glUniform3f(loc_light_pos, math.cos(ang) * 4, 0.0, math.sin(ang) * 4)  ### posicao da fonte de luz

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glClearColor(0.2, 0.2, 0.2, 1.0)

    if polygonal_mode == True:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    if polygonal_mode == False:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    for idx,obj in enumerate(model_infos):
        obj_geo = model_geometrical_init_infos[idx]
        mat_model = model(obj_geo['a'], obj_geo['r'][0], obj_geo['r'][1], obj_geo['r'][2], obj_geo['t'][0], obj_geo['t'][1], obj_geo['t'][2], obj_geo['s'][0], obj_geo['s'][1], obj_geo['s'][2])
        loc_model = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
        loc_ka = glGetUniformLocation(program, "ka")
        glUniform1f(loc_ka, obj_geo['ka'])

        loc_kd = glGetUniformLocation(program, "kd")
        glUniform1f(loc_kd, obj_geo['kd'])
        glBindTexture(GL_TEXTURE_2D, idx)

        # desenha o modelo
        glDrawArrays(GL_TRIANGLES, obj['init'], obj['last'])  ## renderizando

    mat_view = view()
    loc_view = glGetUniformLocation(program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_TRUE, mat_view)

    mat_projection = projection()
    loc_projection = glGetUniformLocation(program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_TRUE, mat_projection)

    glfw.swap_buffers(window)

glfw.terminate()