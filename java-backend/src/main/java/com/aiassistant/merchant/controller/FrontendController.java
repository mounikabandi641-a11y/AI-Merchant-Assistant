package com.aiassistant.merchant.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class FrontendController {
    @GetMapping({
        "/{path:^(?!api$|transactions$|disputes$|health$|assets$)[^.]+$}",
        "/{path:^(?!api$|transactions$|disputes$|health$|assets$)[^.]+$}/**"
    })
    public String forwardToReactApp() {
        return "forward:/index.html";
    }
}