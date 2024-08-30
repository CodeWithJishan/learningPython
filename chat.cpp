#include <iostream>
#include <thread>
#include <cstdlib>
#include <ctime>
#include <string>
#include <cstring>
#include <random>
#include <unistd.h>
#include <cstdio>

std::string generate_random_key(size_t length) {
    const std::string characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    std::string key;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, characters.size() - 1);

    for (size_t i = 0; i < length; ++i) {
        key += characters[dis(gen)];
    }

    return key;
}

bool verify_password(const std::string& compromise_password) {
    std::string entered_password;
    const int max_attempts = 3;

    for (int attempt = 0; attempt < max_attempts; ++attempt) {
        std::cout << "Enter your compromise password: ";
        std::getline(std::cin, entered_password);

        if (entered_password == compromise_password) {
            std::cout << "Password verified. Chat unlocked." << std::endl;
            return true;
        } else {
            std::cout << "Incorrect password. Try again." << std::endl;
        }
    }

    std::cout << "Too many incorrect attempts. Exiting..." << std::endl;
    return false;
}

void start_listener(const std::string& key, int port) {
    std::string listener_command = "cryptcat -k " + key + " -l -p " + std::to_string(port);
    std::cout << "Listening on port " << port << " with encryption key: " << key << std::endl;
    int result = system(listener_command.c_str());
    if (result != 0) {
        std::cerr << "Error starting listener." << std::endl;
    }
}

void send_message(const std::string& target_ip, const std::string& key, int port) {
    std::string message;
    while (true) {
        std::cout << "You: ";
        std::getline(std::cin, message);

        if (message == "exit") {
            std::cout << "Exiting chat..." << std::endl;
            break;
        }

        std::string send_command = "echo " + message + " | cryptcat -k " + key + " " + target_ip + " " + std::to_string(port);
        int result = system(send_command.c_str());
        if (result != 0) {
            std::cerr << "Error sending message." << std::endl;
            break;
        }
    }
}

int main() {
    const std::string compromise_password = "cookie10";  // Set your compromise password here
    const int port = 1234;
    std::string key = generate_random_key(16);

    // Verify the user's password before starting chat
    if (!verify_password(compromise_password)) {
        return 1;  // Exit if the password verification fails
    }

    // Get the target IP address to connect to
    std::string target_ip;
    std::cout << "Enter the IP address to connect to: ";
    std::getline(std::cin, target_ip);

    // Start listener in a separate thread to handle incoming messages
    std::thread listener_thread(start_listener, key, port);
    listener_thread.detach();  // Detach the thread to run independently

    // Start sending messages
    send_message(target_ip, key, port);

    return 0;
}
