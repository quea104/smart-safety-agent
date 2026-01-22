package com.example.safetybackend.controller;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/safety")
@CrossOrigin(origins = "*") // 테스트용 CORS 허용
public class SafetyController {

    private final String AI_SERVER_URL = "http://localhost:8000/ask";

    @PostMapping("/query")
    public ResponseEntity<?> askQuestion(@RequestBody Map<String, String> request) {
        String query = request.get("query");

        // 1. Python 서버로 전송할 데이터 준비
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> aiRequest = new HashMap<>();
        aiRequest.put("query", query);

        HttpEntity<Map<String, String>> entity = new HttpEntity<>(aiRequest, headers);

        // 2 Python 서버 호출 및 응답 수신
        try {
            ResponseEntity<String> response = restTemplate.postForEntity(AI_SERVER_URL, entity, String.class);
            System.out.println(response.getBody());
            return ResponseEntity.ok(response.getBody());
        } catch (Exception e) {
            return ResponseEntity.status(500).body("AI 서버 연결 실패 " + e.getMessage());
        }
    }

}
