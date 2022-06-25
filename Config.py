import glfw
from OpenGL.GL import *


def config():
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
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
