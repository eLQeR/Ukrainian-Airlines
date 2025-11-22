# Ukrainian Airlines Android App

A modern Android application for booking flights with Ukrainian Airlines, built with Kotlin and following Google Material Design 3 guidelines.

## Features

- **Flight Search**: Search for flights between airports with date selection
- **Flight Booking**: Book flights with passenger details
- **User Authentication**: Register and login with JWT tokens
- **Order Management**: View and manage your flight bookings
- **Material Design 3**: Modern UI following Google's design guidelines
- **Kiwi Airlines Inspired**: Clean, intuitive interface similar to popular flight booking apps

## Architecture

The app follows the MVVM (Model-View-ViewModel) architecture pattern:

- **Models**: Data classes representing API responses
- **Views**: Fragments with Material Design 3 UI components
- **ViewModels**: Business logic and data management with LiveData
- **Repository**: Data access layer with Retrofit API calls

## Tech Stack

- **Language**: Kotlin
- **Architecture**: MVVM
- **Networking**: Retrofit 2 with OkHttp
- **UI**: Material Design 3, View Binding, Navigation Component
- **Async**: Coroutines and LiveData
- **Dependency Injection**: Manual (can be upgraded to Hilt/Dagger)

## API Integration

The app integrates with a Django REST API backend providing:

- Flight search and booking
- User authentication (JWT)
- Order management
- Airport and route data

## Getting Started

1. **Prerequisites**:
   - Android Studio Arctic Fox or later
   - Minimum SDK: API 24 (Android 7.0)
   - Target SDK: API 34 (Android 14)

2. **Setup**:
   - Clone the repository
   - Open the `android_app` folder in Android Studio
   - Build and run on device/emulator

3. **Backend Setup**:
   - Ensure the Django backend is running on `http://10.0.2.2:8000` (Android emulator)
   - For physical devices, update the BASE_URL in `UkrainianAirlinesApi.kt`

## Project Structure

```
app/src/main/java/com/example/ukrainianairlines/
├── data/
│   ├── api/           # Retrofit API interfaces
│   ├── model/         # Data classes
│   └── repository/    # Data repositories
├── ui/
│   ├── screens/       # Fragments
│   └── viewmodels/    # ViewModels
└── utils/             # Utility classes
```

## Key Components

### API Layer
- `UkrainianAirlinesApi`: Retrofit interface for all API calls
- JWT authentication with automatic token refresh
- Comprehensive error handling

### UI Components
- Material Design 3 theming
- Bottom navigation with search, bookings, and profile
- Responsive layouts for different screen sizes
- Loading states and error handling

### Data Management
- Repository pattern for data operations
- LiveData for reactive UI updates
- Coroutines for asynchronous operations

## Best Practices Implemented

- **Google Android Guidelines**: Following official Android development best practices
- **Material Design 3**: Latest design system with dynamic theming
- **Kotlin**: Modern language features and null safety
- **Clean Architecture**: Separation of concerns with MVVM
- **Error Handling**: Comprehensive error states and user feedback
- **Accessibility**: Screen reader support and touch targets
- **Performance**: Efficient RecyclerView usage and background operations

## Future Enhancements

- [ ] Seat selection interface
- [ ] Payment integration
- [ ] Push notifications
- [ ] Offline support
- [ ] Multi-language support
- [ ] Dark theme
- [ ] Biometric authentication

## Contributing

1. Follow the established architecture patterns
2. Write tests for new features
3. Update documentation
4. Follow Kotlin coding standards
5. Use meaningful commit messages

## License

This project is part of the Ukrainian Airlines system.