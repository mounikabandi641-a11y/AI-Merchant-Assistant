package com.aiassistant.merchant.config;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${FRONTEND_ORIGIN:}")
    private String frontendOrigin;

    @Override
    public void addCorsMappings(CorsRegistry registry) {

        List<String> allowedOrigins = new ArrayList<>(List.of(
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost"
        ));

        String configuredOrigin = frontendOrigin.trim();

        if (!configuredOrigin.isEmpty() &&
            !allowedOrigins.contains(configuredOrigin)) {
            allowedOrigins.add(configuredOrigin);
        }

        registry.addMapping("/**")
            .allowedOriginPatterns(
                "https://*.vercel.app",
                "https://*.onrender.com",
                "http://localhost:*",
                "http://127.0.0.1:*"
            )
            .allowedMethods(
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
                "OPTIONS"
            )
            .allowedHeaders("*");
    }
}