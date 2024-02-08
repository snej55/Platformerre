#version 330 core

uniform sampler2D tex;
// use a different noise texture e.g: different scale, detail, size, octaves, levels
uniform sampler2D noise;
uniform sampler2D alpha_surf; // smoke vfx... etc
uniform sampler2D ui_surf;
//uniform sampler2D bloom_tex;
uniform float time;
// scroll (obsolete)
uniform vec2 camera;

in vec2 uvs; // pixel coordinates
out vec4 f_color;  // pixel color

uniform float timeScale = 0.0001;  // time speed
// messy stuff ---------
uniform float angleConst = 1.5;
uniform float stripeImpact = 0.03;
uniform float stripeWidth = 60;
uniform float bloom_threshold = 0.2;
uniform float bloom_weight = 0.25;
uniform float weight[7] = float[] (0.227027, 0.2, 0.17, 0.1216216, 0.08, 0.03, 0.016216);
// ---------------------
uniform float threshold = 0.43; // size of hole

vec4 bitFilter(vec4 color) {
    vec4 bloom_color = color;
    float alpha = (bloom_color.r + bloom_color.g + bloom_color.g) * 0.333;
    if (alpha < bloom_threshold) {
        bloom_color.rgb = vec3(0.0, 0.0, 0.0);
    } 
    return bloom_color;
}

vec4 sampleTex(vec2 coords) {
    return bitFilter(texture(tex, coords) + texture(alpha_surf, coords));
}

void main() {
    float centerDis = distance(vec2(0.5, 0.5), uvs);
    centerDis = centerDis * centerDis * centerDis * centerDis * 0.2;
    vec2 texCoords = vec2(uvs.x, uvs.y);  // can be used to warp screen
    vec2 noise_offset = vec2(texture(noise, vec2(texCoords.x, texCoords.y - time * timeScale)).r) * 0.5; 
    vec4 baseColor;
    vec4 noiseColor = texture(noise, texCoords * 2 - noise_offset);
    vec4 hillColor = texture(noise, texCoords * 0.5 - noise_offset * 0.5);
    vec4 combinedColor = (noiseColor + hillColor * 2) * 0.333;
    // manipulate noise texture based on time --------------------------------------------------
    /*vec2 shiftTexcoords = vec2(texCoords.x + sin(time * 0.2 * timeScale), texCoords.y * 2.0 - sin(time * 0.02 * timeScale)); // change stuff here
    vec4 color1 = texture(noise, shiftTexcoords);
    
    shiftTexcoords = vec2(texCoords.x * 2.7 - sin(time * 0.05 * timeScale), texCoords.y * 1.7 - sin(time * 0.5 * timeScale)); // and here
    vec4 color2 = texture(noise, shiftTexcoords);

    shiftTexcoords = vec2(texCoords.x * 0.35 - sin(time * 0.4 * timeScale), texCoords.y * 0.35 - sin(time * 0.4 * timeScale)); // here as well
    vec4 color3 = texture(noise, shiftTexcoords);
    // -----------------------------------------------------------------------------------------

    // some funky math
    vec4 combinedColor = (color1 + color2 * 0.5 + color3 * 0.5) * 0.5;
    combinedColor = combinedColor * (distance(vec2(0.5, 0.5), texCoords) * 0.5 + 0.5) + sin((texCoords.x - texCoords.y * angleConst) * stripeWidth) * stripeImpact;
    */
    if (combinedColor.r < threshold) {
        // reflections
        float center_dis =  (distance(vec2(0.5, 0.5), texCoords * 5) - 0.5) * 0.2 + 0.8;
        vec2 reflectionCoords = vec2((texCoords.x - 0.5) * center_dis + 0.5, (texCoords.y - 0.5) * center_dis + 0.5);
        vec4 reflectionColor = texture(tex, reflectionCoords) * (0.5 - centerDis);
        if (reflectionColor.a == 0) {
            baseColor = vec4(0.025 + reflectionColor.g * 0.1, 0.025 + reflectionColor.b * 0.1, 0.045 + reflectionColor.r * 0.1, 1.0);//baseColor = vec4(0.012, 0.012, 0.025, 1.0);
        } else {
            baseColor = vec4(0.025 + reflectionColor.g * 0.1, 0.025 + reflectionColor.b * 0.1, 0.045 + reflectionColor.r * 0.1, 1.0);
        }
    } else if (combinedColor.r < threshold + 0.01) {
        baseColor = vec4(0.27450980392156865, 0.3568627450980392, 0.9058823529411765, 1.0);  // different colors
    } else if (combinedColor.r < threshold + 0.02) {
        baseColor = vec4(0.27450980392156865, 0.3568627450980392, 0.9058823529411765, 1.0);
    } else if (combinedColor.r < threshold + 0.05) {
        baseColor = vec4(0.13333333333333333, 0.17647058823529413, 0.5058823529411764, 1.0);
    } else if (combinedColor.r < threshold + 0.1) {
        baseColor = vec4(0.10588235294117647, 0.09411764705882353, 0.3254901960784314, 1.0);
    } else {
        baseColor = vec4(0.054901960784313725, 0.03529411764705882, 0.1843137254901961, 1.0);
    }

    // check if part of background
    float alpha = (texture(tex, texCoords).r + texture(tex, texCoords).g + texture(tex, texCoords).b) * 0.333;
    if (alpha > 0.001) {
        baseColor = texture(tex, texCoords);
    }
    // vignait effect
    baseColor = baseColor - centerDis;
    //bloom?
    /*vec4 color = texture(tex, vec2(texCoords.x + 0.02, texCoords.y + 0.02));
    baseColor += bit_filter(color) * 0.5;
    color = texture(tex, vec2(texCoords.x - 0.02, texCoords.y + 0.02));
    baseColor += bit_filter(color) * 0.5;
    color = texture(tex, vec2(texCoords.x + 0.02, texCoords.y - 0.02));
    baseColor += bit_filter(color) * 0.5;
    color = texture(tex, vec2(texCoords.x - 0.02, texCoords.y - 0.02));
    baseColor += bit_filter(color) * 0.5;
    */
    vec4 alpha_sample = texture(alpha_surf, texCoords);
    baseColor += alpha_sample;
    //vec4 bloom_sample = texture(bloom_tex, texCoords);
    //baseColor = bloom_sample;
    vec2 tex_offset = bloom_weight / textureSize(tex, 0);
    vec3 result = bitFilter(texture(tex, texCoords) + texture(alpha_surf, texCoords)).rgb * weight[0];
    for (int i = 1; i < 7; i++) {
        result += sampleTex(texCoords + vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
        result += sampleTex(texCoords - vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
        result += sampleTex(texCoords + vec2(0.0, tex_offset.y * i)).rgb * weight[i];
        result += sampleTex(texCoords - vec2(0.0, tex_offset.y * i)).rgb * weight[i];
    }
    baseColor.rgb += result;
    float ui_alpha = (texture(ui_surf, texCoords).r + texture(ui_surf, texCoords).g + texture(ui_surf, texCoords).b) * 0.333;
    if (ui_alpha > 0.001) {
        baseColor = texture(ui_surf, texCoords);
    }
    f_color = vec4(baseColor.rgb, 1.0);
}