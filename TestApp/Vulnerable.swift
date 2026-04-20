import Foundation
func login(user: String, pass: String) {
    UserDefaults.standard.set(pass, forKey: "user_password")
    print("User logged in with password: \(pass)")
}