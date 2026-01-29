#version 330 core

uniform sampler2D tex;
uniform sampler2D alpha_surf;
uniform sampler2D ui_surf;

in vec2 uvs;
out vec4 f_color;

void main() {
    vec4 baseColor = vec4(texture(tex, uvs).rgb, 1.0);
    baseColor += vec4(texture(alpha_surf, uvs).rgb, 1.0);

    f_color = baseColor;
}