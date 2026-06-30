$dirs = Get-ChildItem "<directory_of_files>" -Directory

foreach ($dir in $dirs) {
    if ($dir.Name -match '\d{8}') {
        $date = $dir.Name
        $partition = $date

        aws s3 sync "$($dir.FullName)" "s3://testbucket/raw/$partition/"
    }
}