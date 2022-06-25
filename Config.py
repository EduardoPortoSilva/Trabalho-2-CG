import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import glm
import math
from PIL import Image


def config():
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    altura = 1600
    largura = 1200
    window = glfw.create_window(largura, altura, "Trabalho 2", None, None)
    glfw.make_context_current(window)
    vertex_code = """
            attribute vec3 position;
            attribute vec2 texture_coord;
            varying vec2 out_texture;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;        

            void main(){
                gl_Position = projection * view * model * vec4(position,1.0);
                out_texture = vec2(texture_coord);
            }
            """
    fragment_code = """
            uniform vec4 color;
            varying vec2 out_texture;
            uniform sampler2D samplerTexture;

            void main(){
                vec4 texture = texture2D(samplerTexture, out_texture);
                gl_FragColor = texture;
            }
            """
    # Request a program and shader slots from GPU
    program = glCreateProgram()
    vertex = glCreateShader(GL_VERTEX_SHADER)
    fragment = glCreateShader(GL_FRAGMENT_SHADER)
    # Set shaders source
    glShaderSource(vertex, vertex_code)
    glShaderSource(fragment, fragment_code)
    # Compile shaders
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
    # Attach shader objects to the program
    glAttachShader(program, vertex)
    glAttachShader(program, fragment)
    # Build program
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        print(glGetProgramInfoLog(program))
        raise RuntimeError('Linking error')

    # Make program the default program
    glUseProgram(program)

    glEnable(GL_TEXTURE_2D)
    qtd_texturas = 10
    textures = glGenTextures(qtd_texturas)

    return program, window, textures
