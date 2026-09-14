# thinking

I find it productive and valuable to write down my thinking as I go along.

## 20260914

I now have in 'plaiground' a mechanism that turns 'simple' eml-file to chime ok.

* But we need to iterate to have the mechanism be able to parse emails with html parts and also process images correctly.

## 20260905

So I am doing some experiemts with Apple Mail to see how I can manually export mails to local storage.

* I now suspect Apple Mail performs these exports in 'the background'
* And maybe the reason Export of my smart mailbox for toto-mails seem to dpo nothing is that it takes time for Apple Mail to perform the upfront processing before any exported files actually appear?

I seem to have two options?

1. Export a mailbox (will create a local mbox-file)
2. Drag emails to a local folder (fill create an eml-file for each mail)

It seems it actually works to drag all my todo-mails from the smart mailbox to a folder?

* For a long time (almost 30 minutes) nothing can be seen on the disk.
* And while Apple Mail works the activity monitor shows Mail at 230% CPU and mdwrite-process at 100%
* And only when all is done can I see the files on the disk.
* Only, Apple Mail created an mbox-file plus a content file?

* So does single file drag-and-drop to folder create an eml-file?
  * YES.
* And multiple drag-and-drop creates an mbox and content file?
  * Drag 2 creates two eml-files.

AHA! Suddenly 4436 files appeared on my disk!

* It must be my drag-and-drop of todo-mails to the disk that finished?

I now realise I have a lot of TODO-mails with the same heading (different revisions of the same todo)

* So Apple Mail crates eml-files with the same file name but suffixed with 1,2,3...

So how do I go about this?

* I can export my smart Todo mail box into a mbox-file
* I can drag-and-drop all my Todo-mails into eml-files

And then it seems I should be able to vibe code some python scripts to process them?

Let's try!

* I do both and get one mbox archive and one set of eml-files?
* Then I can process them with python scripts?
* I then have three representations of my Todo-mails?
* And can see if I can make them all agree on the number of Todo-mails I have?

It seems there is quite a lot of data?

* The eml-file folder is 4,45 GB!
* The mbox file was about 2,5 GB (if I remember correctly?)

I can create scripts from_emls.py and from_mbox.py?

* Preferrably also add a 'cache' storage to enble the scripts to onlyu process changes?

It is now 11:35 and I have initiated both a drag-and-drop of all my over 4500 Todo-mails as well as export of the Todo samrt mail-box.

* Let's see how long this takes and what the end result is?
* 12:04 (+30 min) 
  * No files or folders can be seen in finder
  * But 'get info' shows mbox 1,22 GB, eml-folder (0 bytes)
* 12:31 ( + 1h)
  * Now shows mbox content and GetInfo shows 2,15 GB
  * Now shows eml-files and GetInfo shows 2,19 GB för this folder (4429 files in folder)
  * Apple Mail activity CPU low
  * Process md_stores at 100% (still going?)

So at this point we have different counts for TODO-mails?

* The from_mail.py finds 4427 Todo mails
* The drag-and-drop creates 4429 eml-files

AHA! Still going (now 4431 eml-files)!

* 12:52 (+ 1:20)
  * eml-folder 'Get Info' shows 4430 Items and 2,19 GB
  * eml-folder z-shell 'find . -type f | wc -l' shows 4429 files
  * eml-folder tree command shows 1 directory, 4429 files.
  * Apple Mail Todo smart folder shows 4438 messages
  * mbox-folder 'Get Info' shows 4 items and 2,15 GB
  * Process md_stores shos 100% CPU (still going?)

At this stage I discovered some eml-files that indicates 'outliers'?

```text
├── BRF Ekbladet Todo - Skräp efter bänkrenoveringar behöver hjälp att slängas (städdag i höst?).eml
├── Owls an bells - make .NET app that reads todo mails and creates a todo-list.eml
├── Re_ Todo_ Spb - as long as we dig up or destroy....eml

├── Todo BRF Ekbladet - Marcella är ledsen på sin trädgård och kvalité på uterum.eml
├── Todo Consider a script for a video about what I have learned about metric threading?.eml
├── Todo DIY Open Oscilloscope - Consider to check out Bitscope on Raspberry Pi? 2.eml
├── Todo DIY Open Oscilloscope - Consider to check out Bitscope on Raspberry Pi?.eml
├── Todo Tha C++ - Consider ways to defines "class" meta-3 value using C++ syntax?.eml
├── Todo Tha C++ - Consider we want to be able to write meta-lambdas (to conveniently inject anonymous meta-code)?.eml
├── Todo. SharedPlanet - Consider an aciticity where we design SPB variants of national flags?.eml
├── Todo; SharedPlanet - Vill du ligga med mig?.eml

```

These are 11 e-mails that does NOT seem to be prefixed 'Todo:' (the ':' is not there...)

* So does this account for Apple Mail 4438 messages vs from_mail 4427 mails?

YES - That would perfectly explain it!

* I have configured the smart mailbox as ``` From contains 'kjell-olov' and 'Subject contains 'Todo' ```
  * And from_mail filters on 'Subject begins with 'Todo:'

GREAT! Always nice to have a map that fits the observations!

## 20260904

It seems I have now succeeded to fix the from_mail.py script?

* It now tries to decode the header text using provided encoding or utf-8, latin-1
  * It even has a fallback to ascii + hex-values for unprintables and unknowns.

For my Todo-mails it now finds 4427 mails.

* While Apple Mail states it finds 4438?

So something may still be off?

* Or Apple Mail count is off for some reason?

I now have to decide if it is 'close enough'?

* Or if I should find a way to export from Apple Mail and somehow compare with what from_mail finds?

So how can I export mails from Applke Mail to some local file format?

* It seems I can export to an mbox-file and then process it by a python script?

It seems nothing happens if I try and export my 'smart' Todo-mailbox in Apple Mail?

* I tried right-click and 'Export Mailbox' on my account.
  * This seems to silently initiate an export in the background?
  * I Apple Finder I can see a folder INBOX.partial.mbox with content that grows if a close and open the folder...
  * This is CONFUSING (opaque) user interface, but ok...

## 20260903

Today I created this repo.

I added an experimental from_mail.py script that scans the configured IMAP account for mails that are 'chimes'.

For now I use it on my own account where mails with the subject 'Todo:...' are in fact my 'chimes'.