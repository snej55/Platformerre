#version 330 core

uniform sampler2D tex;
uniform sampler2D alpha_surf;
uniform sampler2D lighting;
uniform sampler2D ui_surf;

in vec2 uvs;
uniform float slomo = 1.0;
out vec4 f_color;

void main() {
    vec4 baseColor = vec4(texture(tex, uvs).rgb, 1.0);

    vec4 lighting_color = vec4(texture(lighting, uvs).rgb, 1.0);
    baseColor -= lighting_color;

    baseColor += vec4(texture(alpha_surf, uvs).rgb, 1.0);

    float grayScale = (baseColor.r + baseColor.b + baseColor.g) * 0.333;
    vec3 averageColor = vec3(grayScale);

    vec3 color = averageColor * (1.0 - slomo) * 0.1 + baseColor.rgb;

    vec3 ui_color = texture(ui_surf, uvs).rgb;
    if (ui_color.r + ui_color.g + ui_color.b > 0.01) {
        color = ui_color;
    }

    f_color = vec4(color, 1.0);
}