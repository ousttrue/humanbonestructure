#version 330
out vec4 FragColor;
in vec2 vUV;
uniform sampler2D Texture;
void main() { FragColor = texture(Texture, vUV); }
