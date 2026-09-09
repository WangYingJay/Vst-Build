; 有品精选插件一键安装包 - 现代深色自定义 UI
#define MyAppId "有品精选插件一键安装包"
#define MyAppVersion "1.0.220410"
#define Password 'youpin001'
#define AppId "{2FE4A8A4-680E-4E1E-B16B-EFB4A1FF0EB6}"

[Setup]
AppId={{#AppId}
AppName={#MyAppId}
AppVerName={#MyAppId}
OutputDir=D:\GLVST
OutputBaseFilename={#MyAppId}
DisableDirPage=yes
Compression=lzma
SolidCompression=yes
DisableWelcomePage=no
DisableReadyPage=yes
SetupIconFile=".\favicon.ico"
ArchitecturesInstallIn64BitMode=x64
CloseApplications=no
CreateAppDir=no
DisableProgramGroupPage=yes
DefaultDirName={src}\Uninstall
AppPublisher=有品测试1
AppVersion={#MyAppVersion}
AppSupportURL=https://www.glbwl.com
AppUpdatesURL=https://www.glbwl.com/gl-vst-wpt.html
VersionInfoDescription=集多厂商高精度64位效果器插件包(直播调试专用)
VersionInfoVersion=1.5
VersionInfoProductName=一键安装
VersionInfoProductTextVersion={#MyAppVersion}
VersionInfoCopyright=有品测试1

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
chinesesimp.installing_label_text=正在安装中

[Dirs]
Name: "{commoncf64}\Avid\Audio\Plug-Ins"; Permissions: users-full
Name: "{commoncf64}\VST3"; Permissions: users-full
Name: "{commonpf64}\VSTPlugins"; Permissions: users-full

[Files]
; botva2=可点击图片按钮；InnoCallback=进度回调；check_ok=完成徽标
Source: "tmp\InnoCallback.dll"; DestDir: {tmp}; Flags: dontcopy
Source: "tmp\botva2.dll"; DestDir: {tmp}; Flags: dontcopy
Source: "tmp\check_ok.bmp"; DestDir: {tmp}; Flags: dontcopy
Source: "tmp\btn_install.png"; DestDir: {tmp}; Flags: dontcopy
Source: "tmp\btn_finish.png"; DestDir: {tmp}; Flags: dontcopy
Source: "tmp\btn_close.png"; DestDir: {tmp}; Flags: dontcopy
; 插件/注册表由 scan_assets.ps1 生成（先运行 scan_assets.ps1 或 build.cmd）
#include "generated\files.inc"

[Run]
#include "generated\run.inc"

[Icons]
Name: "{commondesktop}\R2R"; Filename: "{commonpf64}\R2R";

[Code]
// 深色 UI：按钮用 botva2（保证可点、文字居中），其余用 VCL Panel/Memo
type
  TBtnEventProc = procedure(h: HWND);
  TPBProc = function(h: HWND; Msg, wParam, lParam: Longint): Longint;

const
  UI_W = 500;
  UI_H = 360;
  UI_PAD = 30;
  BTN_CLICK = 1;

  C_BG      = $1B1818;
  C_SURFACE = $2A2727;
  C_BORDER  = $463F3F;
  C_ACCENT  = $81B910;
  C_TITLE   = $F5F4F4;
  C_SUB     = $AAA1A1;
  C_LOG_BG  = $0B0909;
  C_LOG_TX  = $7A7171;

var
  LBrand, LSub, LPwdHint, LStatus, LPercent, LLogHint, LDoneTitle, LDoneSub, LDrag: TLabel;
  PPwdFrame, PPwdInner, PTrack, PFill, PLogFrame: TPanel;
  MemoLog: TNewMemo;
  ImgCheck: TBitmapImage;
  PwdEdit: TPasswordEdit;
  BtnInstall, BtnFinish, BtnClose: HWND;
  glvst_mima_anniu: TNotifyEvent;
  PBOldProc: Longint;
  UiReady: Boolean;

function SetWindowLong(h: HWND; Index: Integer; NewLong: Longint): Longint;
  external 'SetWindowLongW@user32.dll stdcall';
function CallWindowProc(lpPrevWndFunc: Longint; h: HWND; Msg: UINT; wParam, lParam: Longint): Longint;
  external 'CallWindowProcW@user32.dll stdcall';
function ReleaseCapture(): Longint;
  external 'ReleaseCapture@user32.dll stdcall';
function PBCallBack(P: TPBProc; ParamCount: Integer): Longword;
  external 'wrapcallback@files:innocallback.dll stdcall delayload';
function WrapBtnCallback(Callback: TBtnEventProc; ParamCount: Integer): Longword;
  external 'wrapcallback@files:innocallback.dll stdcall delayload';
function BtnCreate(hParent: HWND; Left, Top, Width, Height: Integer; FileName: PAnsiChar; ShadowWidth: Integer; IsCheckBtn: Boolean): HWND;
  external 'BtnCreate@files:botva2.dll stdcall delayload';
procedure BtnSetVisibility(h: HWND; Value: Boolean);
  external 'BtnSetVisibility@files:botva2.dll stdcall delayload';
procedure BtnSetEvent(h: HWND; EventID: Integer; Event: Longword);
  external 'BtnSetEvent@files:botva2.dll stdcall delayload';
procedure BtnSetPosition(h: HWND; NewLeft, NewTop, NewWidth, NewHeight: Integer);
  external 'BtnSetPosition@files:botva2.dll stdcall delayload';
procedure gdipShutdown();
  external 'gdipShutdown@files:botva2.dll stdcall delayload';

procedure AutoCleanBeforeInstall; forward;
procedure AppendLog(const S: String); forward;

procedure FlatPanel(P: TPanel; Clr: TColor; ALeft, ATop, AWidth, AHeight: Integer);
begin
  P.Parent := WizardForm;
  P.BevelOuter := bvNone;
  P.BevelInner := bvNone;
  P.Color := Clr;
  P.SetBounds(ALeft, ATop, AWidth, AHeight);
end;

procedure StyleLabelEx(L: TLabel; const Cap: String; FSize: Integer; FColor: TColor;
  ALeft, ATop, AWidth, AHeight: Integer; Center: Boolean);
begin
  L.Parent := WizardForm;
  L.AutoSize := False;
  L.Transparent := True;
  L.Caption := Cap;
  L.Font.Name := '微软雅黑';
  L.Font.Size := FSize;
  L.Font.Color := FColor;
  L.SetBounds(ALeft, ATop, AWidth, AHeight);
  if Center then L.Alignment := taCenter else L.Alignment := taLeftJustify;
end;

procedure AppendLog(const S: String);
begin
  if (not UiReady) or (MemoLog = nil) then Exit;
  MemoLog.Lines.Add(S);
  MemoLog.SelStart := Length(MemoLog.Text);
  MemoLog.SelLength := 0;
end;

procedure SetProgress(Percent: Integer);
var
  W: Integer;
begin
  if Percent < 0 then Percent := 0;
  if Percent > 100 then Percent := 100;
  LPercent.Caption := IntToStr(Percent) + '%';
  W := (PTrack.Width * Percent) div 100;
  if (Percent > 0) and (W < 2) then W := 2;
  PFill.Color := C_ACCENT;
  PTrack.Color := C_SURFACE;
  PFill.SetBounds(PTrack.Left, PTrack.Top, W, PTrack.Height);
end;

procedure ShowWelcomePage(ShowIt: Boolean);
begin
  LPwdHint.Visible := ShowIt;
  PPwdFrame.Visible := ShowIt;
  PPwdInner.Visible := ShowIt;
  PwdEdit.Visible := ShowIt;
  if ShowIt then
  begin
    PwdEdit.Left := UI_PAD + 12;
    PwdEdit.Top := 138;
    BtnSetVisibility(BtnInstall, True);
    BtnSetPosition(BtnInstall, UI_PAD, 210, 440, 45);
  end
  else
  begin
    PwdEdit.Left := -5000;
    BtnSetVisibility(BtnInstall, False);
    BtnSetPosition(BtnInstall, -5000, 0, 440, 45);
  end;
end;

procedure ShowInstallPage(ShowIt: Boolean);
begin
  LStatus.Visible := ShowIt;
  LPercent.Visible := ShowIt;
  PTrack.Visible := ShowIt;
  PFill.Visible := ShowIt;
  LLogHint.Visible := ShowIt;
  if ShowIt then
  begin
    PLogFrame.Left := UI_PAD;
    PLogFrame.Top := 170;
    MemoLog.Left := UI_PAD + 1;
    MemoLog.Top := 171;
    MemoLog.Visible := True;
    PLogFrame.Visible := True;
  end
  else
  begin
    // 隐藏日志面板
    PLogFrame.Left := -5000;
    MemoLog.Left := -5000;
    MemoLog.Visible := False;
    PLogFrame.Visible := False;
  end;
end;

procedure ShowFinishPage(ShowIt: Boolean);
begin
  ImgCheck.Visible := ShowIt;
  LDoneTitle.Visible := ShowIt;
  LDoneSub.Visible := ShowIt;
  if ShowIt then
  begin
    BtnSetVisibility(BtnFinish, True);
    BtnSetPosition(BtnFinish, (UI_W - 140) div 2, 280, 140, 42);
  end
  else
  begin
    BtnSetVisibility(BtnFinish, False);
    BtnSetPosition(BtnFinish, -5000, 0, 140, 42);
  end;
end;

procedure UI_DragMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Integer);
begin
  ReleaseCapture();
  SendMessage(WizardForm.Handle, $0112, $F012, 0);
end;

procedure OnBtnInstall(hBtn: HWND);
begin
  WizardForm.NextButton.OnClick(WizardForm);
end;

procedure OnBtnFinish(hBtn: HWND);
begin
  WizardForm.NextButton.OnClick(WizardForm);
end;

procedure OnBtnClose(hBtn: HWND);
begin
  if WizardForm.CurPageID = wpFinished then
    WizardForm.NextButton.OnClick(WizardForm)
  else
    WizardForm.CancelButton.OnClick(WizardForm);
end;

procedure UI_PwdEnter(Sender: TObject);
begin
  PPwdFrame.Color := C_ACCENT;
end;

procedure UI_PwdExit(Sender: TObject);
begin
  PPwdFrame.Color := C_BORDER;
end;

function glvst_mima: Boolean;
begin
  Result := (PwdEdit.Text = '{#Password}');
end;

procedure mimaButtonClick(Sender: TObject);
begin
  if WizardForm.CurPageID = wpWelcome then
  begin
    if not glvst_mima then
      MsgBox('密码错误', mbError, MB_OK)
    else
    begin
      AutoCleanBeforeInstall;
      AppendLog('[' + GetDateTimeString('hh:nn:ss', #0, #0) + '] 密码验证通过，开始安装');
      glvst_mima_anniu(Sender);
    end;
  end
  else
    glvst_mima_anniu(Sender);
end;

function PBProc(h: HWND; Msg, wParam, lParam: Longint): Longint;
var
  pr, i1, i2: Extended;
begin
  Result := CallWindowProc(PBOldProc, h, Msg, wParam, lParam);
  if (Msg = $402) and (WizardForm.ProgressGauge.Position > WizardForm.ProgressGauge.Min) then
  begin
    i1 := WizardForm.ProgressGauge.Position - WizardForm.ProgressGauge.Min;
    i2 := WizardForm.ProgressGauge.Max - WizardForm.ProgressGauge.Min;
    if i2 <= 0 then pr := 0 else pr := (i1 * 100) / i2;
    SetProgress(Round(pr));
  end;
end;

procedure LogBeforeFile;
begin
  AppendLog('[' + GetDateTimeString('hh:nn:ss', #0, #0) + '] 正在写入: ' + CurrentFileName);
end;

procedure LogAfterFile;
begin
  AppendLog('[' + GetDateTimeString('hh:nn:ss', #0, #0) + '] 完成: ' + ExtractFileName(CurrentFileName));
end;

procedure KillPluginHosts;
var
  ResultCode: Integer;
begin
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "Studio One.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "Ableton Live 12 Suite.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "Ableton Live 11 Suite.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "Ableton Live 10 Suite.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "Cubase14.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "Cubase13.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "Cubase12.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "FL64.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "REAPER.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "BitwigStudio.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "Waveform12.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "Waveform11.exe" /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

function PendingEntryIsOurs(const S: String): Boolean;
var
  L: String;
begin
  L := LowerCase(S);
  Result := (Pos('\vst3\', L) > 0) or (Pos('/vst3/', L) > 0) or (Pos('\vstplugins\', L) > 0);
end;

procedure ClearVstPendingRenames;
var
  Data, NewData, Cur: String;
  I, N: Integer;
  List: TStringList;
  Drop: Boolean;
begin
  if not RegQueryMultiStringValue(HKLM,
      'SYSTEM\CurrentControlSet\Control\Session Manager',
      'PendingFileRenameOperations', Data) then Exit;
  List := TStringList.Create;
  try
    Cur := '';
    for I := 1 to Length(Data) do
    begin
      if Data[I] = #0 then begin List.Add(Cur); Cur := ''; end
      else Cur := Cur + Data[I];
    end;
    if Cur <> '' then List.Add(Cur);
    NewData := '';
    I := 0; N := List.Count;
    while I < N do
    begin
      Drop := PendingEntryIsOurs(List[I]);
      if (I + 1 < N) and PendingEntryIsOurs(List[I + 1]) then Drop := True;
      if not Drop then
      begin
        NewData := NewData + List[I] + #0;
        if I + 1 < N then NewData := NewData + List[I + 1] + #0;
      end;
      I := I + 2;
    end;
    if NewData = '' then
      RegDeleteValue(HKLM, 'SYSTEM\CurrentControlSet\Control\Session Manager', 'PendingFileRenameOperations')
    else
      RegWriteMultiStringValue(HKLM, 'SYSTEM\CurrentControlSet\Control\Session Manager', 'PendingFileRenameOperations', NewData);
  finally
    List.Free;
  end;
end;

procedure SafeDeleteFile(const FileName: String);
begin
  if (FileName <> '') and FileExists(FileName) then DeleteFile(FileName);
end;

procedure SafeDeletePattern(const Dir, Pattern: String);
var
  ResultCode: Integer;
begin
  if (Dir = '') or (not DirExists(Dir)) then Exit;
  Exec(ExpandConstant('{cmd}'),
    '/C if exist "' + Dir + '\' + Pattern + '" del /f /q "' + Dir + '\' + Pattern + '"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure SafeDeletePatternRecursive(const Dir, Pattern: String);
var
  ResultCode: Integer;
begin
  if (Dir = '') or (not DirExists(Dir)) then Exit;
  Exec(ExpandConstant('{cmd}'),
    '/C if exist "' + Dir + '\' + Pattern + '" del /s /f /q "' + Dir + '\' + Pattern + '"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure DeleteOldPlugins;
var
  BaseVst3, BaseVst2: String;
begin
  BaseVst3 := ExpandConstant('{commoncf64}\VST3');
  if (BaseVst3 <> '') and DirExists(BaseVst3) then
  begin
    SafeDeletePatternRecursive(BaseVst3, '*.vst3');
    SafeDeletePatternRecursive(BaseVst3, '*.tmp');
  end;
  BaseVst2 := ExpandConstant('{commonpf64}\VSTPlugins');
  if (BaseVst2 <> '') and DirExists(BaseVst2) then
  begin
    SafeDeletePatternRecursive(BaseVst2, '*.dll');
    SafeDeletePatternRecursive(BaseVst2, '*.vst');
    SafeDeletePatternRecursive(BaseVst2, '*.tmp');
  end;
end;

procedure AutoCleanBeforeInstall;
begin
  AppendLog('[' + GetDateTimeString('hh:nn:ss', #0, #0) + '] 清理占用进程与旧插件...');
  KillPluginHosts;
  Sleep(400);
  ClearVstPendingRenames;
  DeleteOldPlugins;
  AppendLog('[' + GetDateTimeString('hh:nn:ss', #0, #0) + '] 清理完成');
end;

function InitializeSetup: Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  if Version.Major < 10 then
  begin
    SuppressibleMsgBox('不支持当前系统，只支持Win 10/11(64位)系统', mbCriticalError, MB_OK, MB_OK);
    Result := False;
    Exit;
  end;
  Result := True;
end;

procedure InitializeWizard();
begin
  ExtractTemporaryFile('InnoCallback.dll');
  ExtractTemporaryFile('botva2.dll');
  ExtractTemporaryFile('check_ok.bmp');
  ExtractTemporaryFile('btn_install.png');
  ExtractTemporaryFile('btn_finish.png');
  ExtractTemporaryFile('btn_close.png');
  UiReady := False;

  with WizardForm.NextButton do
  begin
    glvst_mima_anniu := OnClick;
    OnClick := @mimaButtonClick;
  end;

  with WizardForm do
  begin
    BorderStyle := bsNone;
    Color := C_BG;
    ClientWidth := UI_W;
    ClientHeight := UI_H;
    OuterNotebook.Hide;
    Bevel.Hide;
    NextButton.Width := 0;
    CancelButton.Width := 0;
    BackButton.Width := 0;
  end;

  with WizardForm.ProgressGauge do
  begin
    Parent := WizardForm;
    Left := -3000; Top := -3000; Width := 8; Height := 8;
    Visible := False;
  end;

  LDrag := TLabel.Create(WizardForm);
  StyleLabelEx(LDrag, '', 9, C_TITLE, 0, 0, UI_W - 40, 56, False);
  LDrag.OnMouseDown := @UI_DragMouseDown;

  LBrand := TLabel.Create(WizardForm);
  StyleLabelEx(LBrand, '有品精选插件包', 20, C_TITLE, UI_PAD, 28, 400, 32, False);
  LBrand.Font.Style := [fsBold];
  LBrand.OnMouseDown := @UI_DragMouseDown;

  LSub := TLabel.Create(WizardForm);
  StyleLabelEx(LSub, '请输入安装密码后开始安装', 10, C_SUB, UI_PAD, 68, 440, 22, False);

  // 关闭按钮 botva2
  BtnClose := BtnCreate(WizardForm.Handle, UI_W - 40, 10, 28, 28,
    ExpandConstant('{tmp}\btn_close.png'), 0, False);
  BtnSetEvent(BtnClose, BTN_CLICK, WrapBtnCallback(@OnBtnClose, 1));

  // 密码区
  LPwdHint := TLabel.Create(WizardForm);
  StyleLabelEx(LPwdHint, '安装密码', 9, C_SUB, UI_PAD, 108, 120, 18, False);

  PPwdFrame := TPanel.Create(WizardForm);
  FlatPanel(PPwdFrame, C_BORDER, UI_PAD, 130, 440, 40);
  PPwdInner := TPanel.Create(WizardForm);
  FlatPanel(PPwdInner, C_SURFACE, UI_PAD + 1, 131, 438, 38);

  PwdEdit := TPasswordEdit.Create(WizardForm);
  with PwdEdit do
  begin
    Parent := WizardForm;
    Font.Name := '微软雅黑';
    Font.Size := 11;
    Font.Color := C_TITLE;
    Color := C_SURFACE;
    BorderStyle := bsNone;
    SetBounds(UI_PAD + 12, 138, 416, 24);
    OnEnter := @UI_PwdEnter;
    OnExit := @UI_PwdExit;
  end;

  // 安装按钮 PNG
  BtnInstall := BtnCreate(WizardForm.Handle, UI_PAD, 210, 440, 45,
    ExpandConstant('{tmp}\btn_install.png'), 0, False);
  BtnSetEvent(BtnInstall, BTN_CLICK, WrapBtnCallback(@OnBtnInstall, 1));

  // 安装进度
  LStatus := TLabel.Create(WizardForm);
  StyleLabelEx(LStatus, '正在安装', 10, C_TITLE, UI_PAD, 108, 200, 20, False);
  LPercent := TLabel.Create(WizardForm);
  StyleLabelEx(LPercent, '0%', 10, C_ACCENT, UI_PAD + 340, 108, 100, 20, False);
  LPercent.Alignment := taRightJustify;

  PTrack := TPanel.Create(WizardForm);
  FlatPanel(PTrack, C_SURFACE, UI_PAD, 136, 440, 8);
  PFill := TPanel.Create(WizardForm);
  FlatPanel(PFill, C_ACCENT, UI_PAD, 136, 0, 8);

  LLogHint := TLabel.Create(WizardForm);
  StyleLabelEx(LLogHint, '安装日志', 9, C_SUB, UI_PAD, 152, 120, 18, False);

  PLogFrame := TPanel.Create(WizardForm);
  FlatPanel(PLogFrame, C_BORDER, -5000, 170, 440, 125);

  MemoLog := TNewMemo.Create(WizardForm);
  with MemoLog do
  begin
    Parent := WizardForm;
    Left := -5000;
    Top := 171;
    Width := 438;
    Height := 123;
    BorderStyle := bsNone;
    Color := C_LOG_BG;
    Font.Name := 'Consolas';
    Font.Size := 9;
    Font.Color := C_LOG_TX;
    ScrollBars := ssVertical;
    ReadOnly := True;
    Visible := False;
  end;

  // 完成页
  ImgCheck := TBitmapImage.Create(WizardForm);
  with ImgCheck do
  begin
    Parent := WizardForm;
    BackColor := C_BG;
    AutoSize := False;
    Stretch := True;
    SetBounds((UI_W - 48) div 2, 100, 48, 48);
    Visible := False;
    try
      Bitmap.LoadFromFile(ExpandConstant('{tmp}\check_ok.bmp'));
    except
    end;
  end;

  LDoneTitle := TLabel.Create(WizardForm);
  StyleLabelEx(LDoneTitle, '安装完成', 18, C_TITLE, UI_PAD, 160, 440, 30, True);
  LDoneTitle.Font.Style := [fsBold];
  LDoneSub := TLabel.Create(WizardForm);
  StyleLabelEx(LDoneSub, '插件已就绪，可在宿主软件中加载使用', 10, C_SUB, UI_PAD, 196, 440, 22, True);

  BtnFinish := BtnCreate(WizardForm.Handle, -5000, 280, 140, 42,
    ExpandConstant('{tmp}\btn_finish.png'), 0, False);
  BtnSetEvent(BtnFinish, BTN_CLICK, WrapBtnCallback(@OnBtnFinish, 1));
  BtnSetVisibility(BtnFinish, False);

  ShowWelcomePage(False);
  ShowInstallPage(False);
  ShowFinishPage(False);

  PBOldProc := SetWindowLong(WizardForm.ProgressGauge.Handle, -4, PBCallBack(@PBProc, 4));
  UiReady := True;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  Log(Format('CurPageID id = %d', [CurPageID]));
  if not UiReady then Exit;

  ShowWelcomePage(False);
  ShowInstallPage(False);
  ShowFinishPage(False);
  BtnSetVisibility(BtnClose, True);

  if CurPageID = wpWelcome then
  begin
    LBrand.Caption := '有品精选插件包';
    LSub.Caption := '请输入安装密码后开始安装';
    LSub.Visible := True;
    ShowWelcomePage(True);
    PwdEdit.BringToFront;
  end;

  if CurPageID = wpInstalling then
  begin
    LBrand.Caption := '有品精选插件包';
    LSub.Caption := '正在安装插件文件，请稍候...';
    LSub.Visible := True;
    LStatus.Caption := CustomMessage('installing_label_text');
    SetProgress(0);
    AppendLog('[' + GetDateTimeString('hh:nn:ss', #0, #0) + '] 开始写入插件文件...');
    ShowInstallPage(True);
    BtnSetVisibility(BtnClose, False);
  end;

  if CurPageID = wpFinished then
  begin
    LBrand.Caption := '有品精选插件包';
    LSub.Visible := False;
    AppendLog('[' + GetDateTimeString('hh:nn:ss', #0, #0) + '] 安装完成');
    ShowFinishPage(True);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    AppendLog('[' + GetDateTimeString('hh:nn:ss', #0, #0) + '] 正在导入注册表...');
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  case PageID of
    wpWelcome: Result := False;
    wpLicense: Result := True;
    wpPassword: Result := True;
    wpInfoBefore: Result := True;
    wpUserInfo: Result := True;
    wpSelectDir: Result := True;
    wpSelectComponents: Result := True;
    wpSelectProgramGroup: Result := True;
    wpSelectTasks: Result := True;
    wpReady: Result := True;
    wpPreparing: Result := True;
    wpInstalling: Result := False;
    wpInfoAfter: Result := True;
    wpFinished: Result := False;
  else
    Result := True;
  end;
end;

procedure DeinitializeSetup();
begin
  if PBOldProc <> 0 then
    SetWindowLong(WizardForm.ProgressGauge.Handle, -4, PBOldProc);
  gdipShutdown;
end;
