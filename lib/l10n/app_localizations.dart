import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_hi.dart';
import 'app_localizations_mr.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('hi'),
    Locale('mr'),
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'Civic App'**
  String get appTitle;

  /// No description provided for @reportIssue.
  ///
  /// In en, this message translates to:
  /// **'Report Issue'**
  String get reportIssue;

  /// No description provided for @submitComplaint.
  ///
  /// In en, this message translates to:
  /// **'Submit Complaint'**
  String get submitComplaint;

  /// No description provided for @reportMunicipalIssue.
  ///
  /// In en, this message translates to:
  /// **'Report Municipal Issue'**
  String get reportMunicipalIssue;

  /// No description provided for @helpImproveCommunity.
  ///
  /// In en, this message translates to:
  /// **'Help improve your community'**
  String get helpImproveCommunity;

  /// No description provided for @addPhotoVideo.
  ///
  /// In en, this message translates to:
  /// **'Add Photo/Video'**
  String get addPhotoVideo;

  /// No description provided for @camera.
  ///
  /// In en, this message translates to:
  /// **'Camera'**
  String get camera;

  /// No description provided for @gallery.
  ///
  /// In en, this message translates to:
  /// **'Gallery'**
  String get gallery;

  /// No description provided for @takePhoto.
  ///
  /// In en, this message translates to:
  /// **'Take a photo'**
  String get takePhoto;

  /// No description provided for @chooseExisting.
  ///
  /// In en, this message translates to:
  /// **'Choose existing'**
  String get chooseExisting;

  /// No description provided for @remove.
  ///
  /// In en, this message translates to:
  /// **'Remove'**
  String get remove;

  /// No description provided for @description.
  ///
  /// In en, this message translates to:
  /// **'Description'**
  String get description;

  /// No description provided for @describeIssueDetail.
  ///
  /// In en, this message translates to:
  /// **'Describe the issue in detail...'**
  String get describeIssueDetail;

  /// No description provided for @aiGeneratedTitle.
  ///
  /// In en, this message translates to:
  /// **'AI Generated Title:'**
  String get aiGeneratedTitle;

  /// No description provided for @autoGenerate.
  ///
  /// In en, this message translates to:
  /// **'Auto Generate'**
  String get autoGenerate;

  /// No description provided for @generating.
  ///
  /// In en, this message translates to:
  /// **'Generating...'**
  String get generating;

  /// No description provided for @location.
  ///
  /// In en, this message translates to:
  /// **'Location'**
  String get location;

  /// No description provided for @manualLocation.
  ///
  /// In en, this message translates to:
  /// **'Manual Location (Optional)'**
  String get manualLocation;

  /// No description provided for @enterSpecificAddress.
  ///
  /// In en, this message translates to:
  /// **'Enter specific address or landmark...'**
  String get enterSpecificAddress;

  /// No description provided for @refreshLocation.
  ///
  /// In en, this message translates to:
  /// **'Refresh location'**
  String get refreshLocation;

  /// No description provided for @submitComplaintButton.
  ///
  /// In en, this message translates to:
  /// **'Submit Complaint'**
  String get submitComplaintButton;

  /// No description provided for @uploadingComplaint.
  ///
  /// In en, this message translates to:
  /// **'Uploading complaint...'**
  String get uploadingComplaint;

  /// No description provided for @complaintSubmittedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Complaint submitted successfully!'**
  String get complaintSubmittedSuccessfully;

  /// No description provided for @complaintSubmittedPdfGenerated.
  ///
  /// In en, this message translates to:
  /// **'Complaint submitted and PDF generated successfully!'**
  String get complaintSubmittedPdfGenerated;

  /// No description provided for @downloadPdf.
  ///
  /// In en, this message translates to:
  /// **'Download PDF'**
  String get downloadPdf;

  /// No description provided for @pdfSavedTo.
  ///
  /// In en, this message translates to:
  /// **'PDF saved to:'**
  String get pdfSavedTo;

  /// No description provided for @downloadFailed.
  ///
  /// In en, this message translates to:
  /// **'Download failed:'**
  String get downloadFailed;

  /// No description provided for @errorFailedSubmit.
  ///
  /// In en, this message translates to:
  /// **'Error: Failed to submit complaint. Status:'**
  String get errorFailedSubmit;

  /// No description provided for @errorCouldNotConnect.
  ///
  /// In en, this message translates to:
  /// **'Error: Could not connect to the server.'**
  String get errorCouldNotConnect;

  /// No description provided for @howToReportIssue.
  ///
  /// In en, this message translates to:
  /// **'How to Report an Issue'**
  String get howToReportIssue;

  /// No description provided for @step1.
  ///
  /// In en, this message translates to:
  /// **'1. Take a clear photo of the issue'**
  String get step1;

  /// No description provided for @step2.
  ///
  /// In en, this message translates to:
  /// **'2. Add a detailed description'**
  String get step2;

  /// No description provided for @step3.
  ///
  /// In en, this message translates to:
  /// **'3. Verify your location'**
  String get step3;

  /// No description provided for @step4.
  ///
  /// In en, this message translates to:
  /// **'4. Submit the complaint'**
  String get step4;

  /// No description provided for @reportForwarded.
  ///
  /// In en, this message translates to:
  /// **'Your report will be automatically forwarded to the appropriate municipal department.'**
  String get reportForwarded;

  /// No description provided for @gotIt.
  ///
  /// In en, this message translates to:
  /// **'Got it'**
  String get gotIt;

  /// No description provided for @permissionsRequired.
  ///
  /// In en, this message translates to:
  /// **'Permissions Required'**
  String get permissionsRequired;

  /// No description provided for @cameraLocationPermissionsNeeded.
  ///
  /// In en, this message translates to:
  /// **'Camera and location permissions are needed to upload complaints.'**
  String get cameraLocationPermissionsNeeded;

  /// No description provided for @cancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// No description provided for @openSettings.
  ///
  /// In en, this message translates to:
  /// **'Open Settings'**
  String get openSettings;

  /// No description provided for @processing.
  ///
  /// In en, this message translates to:
  /// **'Processing...'**
  String get processing;

  /// No description provided for @pleaseCapturePhotoFirst.
  ///
  /// In en, this message translates to:
  /// **'Please capture or select a photo first.'**
  String get pleaseCapturePhotoFirst;

  /// No description provided for @failedToGenerateDescription.
  ///
  /// In en, this message translates to:
  /// **'Failed to generate description. Please try again.'**
  String get failedToGenerateDescription;

  /// No description provided for @aiError.
  ///
  /// In en, this message translates to:
  /// **'AI error:'**
  String get aiError;

  /// No description provided for @voiceRecordingComingSoon.
  ///
  /// In en, this message translates to:
  /// **'Voice recording feature coming soon!'**
  String get voiceRecordingComingSoon;

  /// No description provided for @sendFunctionalityComingSoon.
  ///
  /// In en, this message translates to:
  /// **'Send functionality coming soon!'**
  String get sendFunctionalityComingSoon;

  /// No description provided for @cameraPermissionDenied.
  ///
  /// In en, this message translates to:
  /// **'Camera permission permanently denied. Please enable it in Settings.'**
  String get cameraPermissionDenied;

  /// No description provided for @locationServicesDisabled.
  ///
  /// In en, this message translates to:
  /// **'Location services disabled'**
  String get locationServicesDisabled;

  /// No description provided for @unableToGetLocation.
  ///
  /// In en, this message translates to:
  /// **'Unable to get location'**
  String get unableToGetLocation;

  /// No description provided for @gettingLocation.
  ///
  /// In en, this message translates to:
  /// **'Getting location...'**
  String get gettingLocation;

  /// No description provided for @readyToSubmit.
  ///
  /// In en, this message translates to:
  /// **'Ready to submit'**
  String get readyToSubmit;

  /// No description provided for @municipalIssue.
  ///
  /// In en, this message translates to:
  /// **'Municipal Issue'**
  String get municipalIssue;

  /// No description provided for @roadInfrastructureIssue.
  ///
  /// In en, this message translates to:
  /// **'Road Infrastructure Issue'**
  String get roadInfrastructureIssue;

  /// No description provided for @streetLightingProblem.
  ///
  /// In en, this message translates to:
  /// **'Street Lighting Problem'**
  String get streetLightingProblem;

  /// No description provided for @waterInfrastructureIssue.
  ///
  /// In en, this message translates to:
  /// **'Water Infrastructure Issue'**
  String get waterInfrastructureIssue;

  /// No description provided for @wasteManagementIssue.
  ///
  /// In en, this message translates to:
  /// **'Waste Management Issue'**
  String get wasteManagementIssue;

  /// No description provided for @trafficManagementIssue.
  ///
  /// In en, this message translates to:
  /// **'Traffic Management Issue'**
  String get trafficManagementIssue;

  /// No description provided for @municipalServiceRequest.
  ///
  /// In en, this message translates to:
  /// **'Municipal Service Request'**
  String get municipalServiceRequest;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @english.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get english;

  /// No description provided for @hindi.
  ///
  /// In en, this message translates to:
  /// **'हिंदी'**
  String get hindi;

  /// No description provided for @marathi.
  ///
  /// In en, this message translates to:
  /// **'मराठी'**
  String get marathi;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'hi', 'mr'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'hi':
      return AppLocalizationsHi();
    case 'mr':
      return AppLocalizationsMr();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
